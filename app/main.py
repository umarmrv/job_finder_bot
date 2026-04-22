from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse 
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
    title="Mekhrobod Jobs Bot API",
    version="0.1.0",
    lifespan=lifespan,
)

# ✅ подключаем роутеры
app.include_router(job_posts_router)
app.include_router(user_router)

@app.get("/", include_in_schema=False)  # ← add this
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def healthcheck():
    return {"status": "ok"}