import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.api.routers import main_router
from app.core import settings
from loguru import logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting app...")

    yield

    logger.info("Application stopped.")


def _include_router(app: FastAPI) -> None:
    app.include_router(main_router.router)


def _add_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS if settings.ALLOW_ORIGINS else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _create_production_app() -> FastAPI:
    logger.info("Creating production app...")
    return FastAPI(
        lifespan=lifespan,
        title="SpyCatAgency_API",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )


def _create_development_app() -> FastAPI:
    logger.info("Creating development app...")
    return FastAPI(
        lifespan=lifespan,
        title="SpyCatAgency_API",
    )


def create_app() -> FastAPI:
    app_factory = (
        _create_production_app if settings.is_production else _create_development_app
    )
    app = app_factory()

    _include_router(app)
    _add_middleware(app)

    return app


if __name__ == "__main__":
    uvicorn.run(
        "app.main:create_app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
    )
