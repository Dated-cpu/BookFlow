from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.application.exceptions import ApplicationError, AuthenticationError
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.engine import close_db, init_db

from src.presentation.api.errors import (
    application_error_handler,
    authentication_error_handler,
    internal_error_handler,
)

from src.presentation.api.v1.routers.appointments import router as appointments_router
from src.presentation.api.v1.routers.auth import router as auth_router
from src.presentation.api.v1.routers.employees import router as employees_router
from src.presentation.api.v1.routers.organizations import router as organizations_router
from src.presentation.api.v1.routers.services import router as services_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = Settings()

    await init_db(settings.database_url)

    yield

    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="BookFlow AI",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://frontend-six-murex-84.vercel.app",
            "https://bookflow-ai.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(
        ApplicationError,
        application_error_handler,
    )

    app.add_exception_handler(
        AuthenticationError,
        authentication_error_handler,
    )

    app.add_exception_handler(
        Exception,
        internal_error_handler,
    )

    app.include_router(
        appointments_router,
        prefix="/api/v1",
    )

    app.include_router(
        auth_router,
        prefix="/api/v1",
    )

    app.include_router(
        organizations_router,
        prefix="/api/v1",
    )

    app.include_router(
        employees_router,
        prefix="/api/v1",
    )

    app.include_router(
        services_router,
        prefix="/api/v1",
    )


    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "service": "BookFlow AI API",
            "status": "running",
        }


    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
        }


    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {
            "status": "ok",
        }


    return app


app = create_app()