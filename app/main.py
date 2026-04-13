from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import engine, Base
from app.routers.job_posts import router as job_posts_router
from app.routers.job_posts import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Jobs Bot API",
    version="0.1.0",
    lifespan=lifespan,
)

# ✅ подключаем роутеры
app.include_router(job_posts_router)
app.include_router(user_router)


@app.get("/health", tags=["Health"])
async def healthcheck():
    return {"status": "ok"}