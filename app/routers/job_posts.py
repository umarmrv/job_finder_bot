from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

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


async def get_job_post_with_users(db: AsyncSession, job_id: int) -> JobPost | None:
    result = await db.execute(
        select(JobPost)
        .options(
            selectinload(JobPost.owner_user),
            selectinload(JobPost.contact_user),
        )
        .where(JobPost.id == job_id)
    )
    return result.scalar_one_or_none()


@router.post("", response_model=JobPostRead, status_code=status.HTTP_201_CREATED)
async def create_job_post(payload: JobPostCreate, db: AsyncSession = Depends(get_db)):
    owner_user_id = payload.user_id or payload.contact_username
    if owner_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User id is required to create a job post",
        )

    owner_user = await db.get(User, owner_user_id)
    if owner_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    contact_user_id = payload.contact_username or owner_user_id
    contact_user = await db.get(User, contact_user_id)
    if contact_user is None:
        raise HTTPException(status_code=404, detail="Contact user not found")

    job_post = JobPost(
        **payload.model_dump(exclude_unset=True, exclude={"user_id", "contact_username"}),
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
    query = select(JobPost).options(
        selectinload(JobPost.owner_user),
        selectinload(JobPost.contact_user),
    )

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
    job_post = await get_job_post_with_users(db, job_id)

    if not job_post:
        raise HTTPException(status_code=404, detail="Job post not found")

    return job_post


@router.patch("/{job_id}", response_model=JobPostRead)
async def update_job_post(job_id: int, payload: JobPostUpdate, db: AsyncSession = Depends(get_db)):
    job_post = await get_job_post_with_users(db, job_id)

    if not job_post:
        raise HTTPException(status_code=404, detail="Job post not found")

    update_data = payload.model_dump(exclude_unset=True)
    next_status = update_data.get("status", job_post.status)

    if "status" in update_data and next_status != job_post.status:
        validate_status_transition(job_post.status, next_status)

    if "published_message_id" in update_data and next_status != JobStatus.published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="published_message_id can be set only for published job posts",
        )

    if "contact_username" in update_data and update_data["contact_username"] is not None:
        contact_user = await db.get(User, update_data["contact_username"])
        if contact_user is None:
            raise HTTPException(status_code=404, detail="Contact user not found")

    for field, value in update_data.items():
        setattr(job_post, field, value)

    await db.commit()
    return await get_job_post_with_users(db, job_post.id)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_post(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobPost).where(JobPost.id == job_id))
    job_post = result.scalar_one_or_none()

    if not job_post:
        raise HTTPException(status_code=404, detail="Job post not found")

    await db.delete(job_post)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -------------------- USERS --------------------

user_router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@user_router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(
        telegram_id=user.telegram_id,
        full_name=user.full_name,
        username=user.username,
        phone=user.phone,
        role=user.role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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
