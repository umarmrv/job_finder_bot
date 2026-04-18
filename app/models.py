import enum
from datetime import datetime, date

from sqlalchemy import Integer, String, BigInteger, DateTime, Enum, Numeric, Text, func, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class JobType(str, enum.Enum):
    vacancy = "vacancy"
    daily_job = "daily_job"


class JobStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    published = "published"
    rejected = "rejected"
    closed = "closed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="employer")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class JobPost(Base):
    __tablename__ = "job_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    job_type: Mapped[JobType] = mapped_column(Enum(JobType, name="job_type_enum"), nullable=False, default=JobType.vacancy)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus, name="job_status_enum"), nullable=False, default=JobStatus.draft)
    salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    workers_needed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    contact_username: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # важно — это твое поле, оставляем
    published_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
