import os

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies.auth import get_current_user
from app.db import get_db
from app.models import User, JobPost, JobStatus, JobType
from app.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
    JobPostCreate,
    JobPostRead,
    JobPostUpdate,
)

# -------------------- JOB POSTS --------------------

router = APIRouter(prefix="/api/v1/job-posts", tags=["Job Posts"])


def _parse_admin_ids(raw_admin_ids: str | None) -> set[int]:
    if not raw_admin_ids:
        return set()

    admin_ids: set[int] = set()
    for value in raw_admin_ids.split(","):
        candidate = value.strip()
        if not candidate:
            continue
        try:
            admin_ids.add(int(candidate))
        except ValueError:
            continue
    return admin_ids


ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS"))


ALLOWED_STATUS_TRANSITIONS = {
    JobStatus.draft: {JobStatus.pending},
    JobStatus.pending: {JobStatus.approved, JobStatus.rejected, JobStatus.closed},
    JobStatus.approved: {JobStatus.published, JobStatus.rejected, JobStatus.closed},
    JobStatus.published: {JobStatus.closed},
    JobStatus.rejected: set(),
    JobStatus.closed: set(),
}


def validate_status_transition(current_status: JobStatus, next_status: JobStatus) -> None:
    allowed_statuses = ALLOWED_STATUS_TRANSITIONS[current_status]
    if next_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {current_status.value} → {next_status.value}",
        )


def _job_post_with_users_query():
    return select(JobPost).options(
        selectinload(JobPost.owner_user),
        selectinload(JobPost.contact_user),
    )


def _raise_not_found(detail: str) -> None:
    raise HTTPException(status_code=404, detail=detail)


def _ensure_job_post_access(current_user: User, job_post: JobPost) -> None:
    if current_user.role == "admin":
        return
    if job_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


def _require_status_for_published_message(next_status: JobStatus) -> None:
    if next_status != JobStatus.published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="published_message_id can be set only for published job posts",
        )


async def _get_user_or_404(db: AsyncSession, user_id: int, detail: str = "User not found") -> User:
    user = await db.get(User, user_id)
    if user is None:
        _raise_not_found(detail)
    return user


async def _get_job_post_or_404(db: AsyncSession, job_id: int) -> JobPost:
    job_post = await get_job_post_with_users(db, job_id)
    if job_post is None:
        _raise_not_found("Job post not found")
    return job_post


async def get_job_post_with_users(db: AsyncSession, job_id: int) -> JobPost | None:
    result = await db.execute(
        _job_post_with_users_query().where(JobPost.id == job_id)
    )
    return result.scalar_one_or_none()


@router.post("", response_model=JobPostRead, status_code=status.HTTP_201_CREATED)
async def create_job_post(payload: JobPostCreate, db: AsyncSession = Depends(get_db)):
    owner_user_id = payload.user_id
    if owner_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User id is required to create a job post",
        )

    owner_user = await _get_user_or_404(db, owner_user_id)

    contact_user_id = payload.contact_username or owner_user_id
    await _get_user_or_404(db, contact_user_id, detail="Contact user not found")

    create_data = payload.model_dump(exclude_unset=True, exclude={"user_id", "contact_username"})
    if "status" not in create_data:
        create_data["status"] = JobStatus.pending
    if create_data.get("contact_phone") is None:
        create_data["contact_phone"] = owner_user.phone

    job_post = JobPost(
        **create_data,
        user_id=owner_user_id,
        contact_username=contact_user_id,
    )
    db.add(job_post)
    await db.commit()
    return await get_job_post_with_users(db, job_post.id)


@router.get("", response_model=list[JobPostRead])
async def list_job_posts(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: JobStatus | None = Query(default=None),
    job_type: JobType | None = Query(default=None),
    city: str | None = Query(default=None, min_length=2, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    query = _job_post_with_users_query()

    if status is not None:
        query = query.where(JobPost.status == status)

    if job_type is not None:
        query = query.where(JobPost.job_type == job_type)

    if city:
        query = query.where(JobPost.city.ilike(f"%{city.strip()}%"))

    result = await db.execute(
        query.order_by(JobPost.created_at.desc(), JobPost.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get("/{job_id}", response_model=JobPostRead)
async def get_job_post(job_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_job_post_or_404(db, job_id)


@router.patch("/{job_id}", response_model=JobPostRead)
async def update_job_post(
    job_id: int,
    payload: JobPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job_post = await _get_job_post_or_404(db, job_id)
    _ensure_job_post_access(current_user, job_post)

    update_data = payload.model_dump(exclude_unset=True)
    next_status = update_data.get("status", job_post.status)

    if "status" in update_data and next_status != job_post.status:
        validate_status_transition(job_post.status, next_status)

    if "published_message_id" in update_data:
        _require_status_for_published_message(next_status)

    if "contact_username" in update_data and update_data["contact_username"] is not None:
        await _get_user_or_404(db, update_data["contact_username"], detail="Contact user not found")

    for field, value in update_data.items():
        setattr(job_post, field, value)

    await db.commit()
    return await get_job_post_with_users(db, job_post.id)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_post(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job_post = await _get_job_post_or_404(db, job_id)
    _ensure_job_post_access(current_user, job_post)
    await db.delete(job_post)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -------------------- USERS --------------------

user_router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@user_router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    forced_role = "admin" if user.telegram_id in ADMIN_IDS else "employer"
    db_user = User(
        telegram_id=user.telegram_id,
        full_name=user.full_name,
        username=user.username,
        phone=user.phone,
        role=forced_role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@user_router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_user_or_404(db, user_id)


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await _get_user_or_404(db, user_id)
    await db.delete(user)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await _get_user_or_404(db, user_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@user_router.get("", response_model=list[UserRead])
async def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.id.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())
