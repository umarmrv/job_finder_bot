
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.models import JobStatus, JobType
from pydantic import BaseModel
from datetime import datetime


class JobPostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    city: str = Field(min_length=2, max_length=100)
    job_type: JobType
    salary: Decimal | None = Field(default=None, ge=0)
    workers_needed: int | None = Field(default=None, ge=1)
    work_date: date | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    contact_username: str | None = Field(default=None, max_length=100)


class JobPostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=10)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    job_type: JobType | None = None
    status: JobStatus | None = None
    salary: Decimal | None = Field(default=None, ge=0)
    workers_needed: int | None = Field(default=None, ge=1)
    work_date: date | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    contact_username: str | None = Field(default=None, max_length=100)


class JobPostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    city: str
    job_type: JobType
    status: JobStatus
    salary: Decimal | None
    workers_needed: int | None
    work_date: date | None
    contact_phone: str | None
    contact_username: str | None
    created_at: datetime
    updated_at: datetime

class UserCreate(BaseModel):
    telegram_id: int
    full_name: str
    username: str
    phone: str
    role: str

class UserRead(BaseModel):
    id: int
    telegram_id: int
    full_name: str
    username: str
    phone: str
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy modeldan o'qish uchun    