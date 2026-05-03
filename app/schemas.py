from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.models import JobStatus, JobType


# -------------------- JobPost --------------------

class JobPostCreate(BaseModel):
    user_id: int | None = Field(default=None, ge=1, description="ID пользователя-владельца вакансии.")
    title: str = Field(min_length=3, max_length=255, description="Короткий заголовок вакансии.")
    description: str = Field(min_length=10, description="Подробное описание обязанностей и условий.")
    city: str = Field(min_length=2, max_length=100, description="Город, где требуется сотрудник.")
    job_type: JobType = Field(description="Тип объявления: постоянная вакансия или разовая работа.")
    status: JobStatus = Field(default=JobStatus.draft, description="Начальный статус публикации.")
    salary: Decimal | None = Field(default=None, ge=0, description="Зарплата или оплата за работу.")
    workers_needed: int | None = Field(default=None, ge=1, description="Количество требуемых работников.")
    work_date: date | None = Field(default=None, description="Дата выхода, если работа на конкретный день.")
    contact_phone: str | None = Field(default=None, max_length=30, description="Контактный номер телефона.")
    contact_username: int | None = Field(default=None, ge=1, description="ID контактного пользователя.")


class JobPostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255, description="Новый заголовок вакансии.")
    description: str | None = Field(default=None, min_length=10, description="Новое описание вакансии.")
    city: str | None = Field(default=None, min_length=2, max_length=100, description="Обновлённый город.")
    job_type: JobType | None = Field(default=None, description="Обновлённый тип объявления.")
    status: JobStatus | None = Field(default=None, description="Новый статус согласно правилам перехода.")
    published_message_id: int | None = Field(
        default=None,
        ge=1,
        description="ID сообщения в канале после публикации (разрешено только для published).",
    )
    published_chat_id: int | None = Field(
        default=None,
        description="ID Telegram канала/чата, где опубликована вакансия.",
    )
    salary: Decimal | None = Field(default=None, ge=0, description="Обновлённая зарплата/оплата.")
    workers_needed: int | None = Field(default=None, ge=1, description="Обновлённое число работников.")
    work_date: date | None = Field(default=None, description="Новая дата выхода на работу.")
    contact_phone: str | None = Field(default=None, max_length=30, description="Новый контактный телефон.")
    contact_username: int | None = Field(default=None, ge=1, description="Новый ID контактного пользователя.")


class JobPostStatusUpdate(BaseModel):
    status: JobStatus = Field(description="Новый бизнес-статус вакансии.")


class JobPostPublishInfo(BaseModel):
    published_message_id: int = Field(ge=1, description="ID опубликованного сообщения в Telegram канале.")
    published_chat_id: int = Field(description="ID Telegram канала/чата (может быть отрицательным).")


class JobPostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="ID вакансии.")
    user_name: str | None = Field(description="Имя владельца вакансии.")
    title: str = Field(description="Заголовок вакансии.")
    description: str = Field(description="Описание вакансии.")
    city: str = Field(description="Город вакансии.")
    job_type: JobType = Field(description="Тип объявления.")
    status: JobStatus = Field(description="Текущий статус вакансии.")
    published_message_id: int | None = Field(description="ID опубликованного сообщения в канале.")
    published_chat_id: int | None = Field(description="ID Telegram канала/чата публикации.")
    salary: Decimal | None = Field(description="Зарплата/оплата.")
    workers_needed: int | None = Field(description="Требуемое количество работников.")
    work_date: date | None = Field(description="Дата работы.")
    contact_phone: str | None = Field(description="Контактный телефон.")
    contact_username: str | None = Field(
        validation_alias="contact_name",
        description="Логин или имя контактного пользователя.",
    )
    created_at: datetime = Field(description="Дата создания записи.")
    updated_at: datetime = Field(description="Дата последнего обновления.")


# -------------------- User --------------------

class UserCreate(BaseModel):
    telegram_id: int = Field(description="Уникальный Telegram ID пользователя.")
    full_name: str = Field(description="Полное имя пользователя.")
    username: str | None = Field(default=None, description="Telegram username без @.")
    phone: str | None = Field(default=None, description="Телефон пользователя.")
    role: str = Field(default="employer", description="Роль пользователя в системе.")


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, description="Новое полное имя.")
    username: str | None = Field(default=None, description="Новый Telegram username.")
    phone: str | None = Field(default=None, description="Новый телефон.")
    role: str | None = Field(default=None, description="Новая роль.")


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Внутренний ID пользователя.")
    telegram_id: int = Field(description="Telegram ID пользователя.")
    full_name: str = Field(description="Полное имя пользователя.")
    username: str | None = Field(description="Telegram username.")
    phone: str | None = Field(description="Телефон пользователя.")
    role: str = Field(description="Роль пользователя.")
    created_at: datetime = Field(description="Дата создания пользователя.")
    updated_at: datetime = Field(description="Дата последнего обновления пользователя.")
