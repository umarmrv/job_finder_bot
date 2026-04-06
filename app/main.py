from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.db import engine, Base
from app import models
from app.routers.job_posts import router as job_posts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте (в dev окружении нормально)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Здесь можно добавить graceful shutdown, если понадобится


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API для Jobs Bot",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    title="Jobs Bot API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)

app.openapi = custom_openapi

# Подключаем роутеры
app.include_router(job_posts_router)

# Кастомная главная страница — Swagger UI
@app.get("/", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/health", tags=["Health"])
async def healthcheck():
    return {"status": "ok", "service": "jobs-bot-api"}
