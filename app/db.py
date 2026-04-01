import os
from typing import AsyncGenerator
from dotenv import load_dotenv  # Добавьте этот импорт
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Загружаем переменные из файла .env
load_dotenv()

# Получаем URL из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверка, что переменная загрузилась, чтобы избежать ошибки "Could not parse"
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в файле .env или переменных окружения")

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
