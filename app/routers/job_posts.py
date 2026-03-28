from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import JobPost
from app.schemas import JobPostCreate, JobPostRead, JobPostUpdate

router = APIRouter(prefix="/api/v1/job-posts", tags=["Job Posts"])


@router.post(
    "",
    response_model=JobPostRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_post(
    payload: JobPostCreate,
    db: AsyncSession = Depends(get_db),
):
    job_post = JobPost(**payload.model_dump())

    db.add(job_post)
    await db.commit()
    await db.refresh(job_post)

    return job_post


@router.get(
    "",
    response_model=list[JobPostRead],
)
async def list_job_posts(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JobPost)
        .order_by(JobPost.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get(
    "/{job_id}",
    response_model=JobPostRead,
)
async def get_job_post(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(JobPost).where(JobPost.id == job_id))
    job_post = result.scalar_one_or_none()

    if not job_post:
        raise HTTPException(status_code=404, detail="Job post not found")

    return job_post


@router.patch(
    "/{job_id}",
    response_model=JobPostRead,
)
async def update_job_post(
    job_id: int,
    payload: JobPostUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(JobPost).where(JobPost.id == job_id))
    job_post = result.scalar_one_or_none()

    if not job_post:
        raise HTTPException(status_code=404, detail="Job post not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_post, field, value)

    await db.commit()
    await db.refresh(job_post)

    return job_post


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job_post(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(JobPost).where(JobPost.id == job_id))
    job_post = result.scalar_one_or_none()

    if not job_post:
        raise HTTPException(status_code=404, detail="Job post not found")

    await db.delete(job_post)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)