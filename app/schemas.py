from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.models import JobStatus, JobType


# -------------------- JobPost --------------------

class JobPostCreate(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    city: str = Field(min_length=2, max_length=100)
    job_type: JobType
    status: JobStatus = JobStatus.draft
    salary: Decimal | None = Field(default=None, ge=0)
    workers_needed: int | None = Field(default=None, ge=1)
    work_date: date | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    contact_username: int | None = Field(default=None, ge=1)


class JobPostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=10)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    job_type: JobType | None = None
    status: JobStatus | None = None
    published_message_id: int | None = Field(default=None, ge=1)
    salary: Decimal | None = Field(default=None, ge=0)
    workers_needed: int | None = Field(default=None, ge=1)
    work_date: date | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    contact_username: int | None = Field(default=None, ge=1)


class JobPostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str
    city: str
    job_type: JobType
    status: JobStatus
    published_message_id: int | None
    salary: Decimal | None
    workers_needed: int | None
    work_date: date | None
    contact_phone: str | None
    contact_username: int | None
    created_at: datetime
    updated_at: datetime


# -------------------- User --------------------

class UserCreate(BaseModel):
    telegram_id: int
    full_name: str
    username: str | None = None
    phone: str | None = None
    role: str = "employer"


class UserUpdate(BaseModel):
    full_name: str | None = None
    username: str | None = None
    phone: str | None = None
    role: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    full_name: str
    username: str | None
    phone: str | None
    role: str
    created_at: datetime
    updated_at: datetime
