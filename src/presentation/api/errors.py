import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.application.exceptions import ApplicationError, AuthenticationError

logger = logging.getLogger(__name__)


async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled internal error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check server logs."},
    )
