import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.errors import (
    ProblemDetails,
    ValidationErrorItem,
    ValidationErrorProblemDetails,
)

from .base import AppError
from .mapping import ErrorMapping

logger = logging.getLogger(__name__)


def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    status_code, schema = ErrorMapping.get_status_code_and_schema(exc)

    logger.warning(
        "Application business exception occurred: %s",
        exc.detail,
        extra={
            "http_status": status_code,
            "error_code": exc.code,
            "path": request.url.path,
            "method": request.method,
            **exc.extra,
        },
    )

    details = schema.model_validate(exc)
    details.status = status_code

    return JSONResponse(
        status_code=status_code,
        content=details.model_dump(mode="json"),
        headers={"Content-Type": "application/problem+json"},
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "Request validation failed at entry point.",
        extra={
            "http_status": 422,
            "error_code": "VALIDATION_ERROR",
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params),
            "invalid_params": exc.errors(),
        },
    )

    details = ValidationErrorProblemDetails(
        title="Unprocessable Entity",
        status=422,
        detail="Invalid data",
        code="VALIDATION_ERROR",
        invalid_params=[ValidationErrorItem.model_validate(error) for error in exc.errors()],
    )

    return JSONResponse(
        status_code=422,
        content=details.model_dump(mode="json"),
        headers={"Content-Type": "application/problem+json"},
    )


def http_exception_handler(request: Request, exc: HTTPException):
    title, code = "HTTP Error", "HTTP_ERROR"

    logger.warning(
        "An HTTP Error occurred.",
        extra={
            "http_status": exc.status_code,
            "error_code": code,
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params),
            "exception_detail": exc.detail,
            "detail": exc.detail,
        },
    )

    details = ProblemDetails(
        title=title,
        status=exc.status_code,
        detail=exc.detail,
        code=code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=details.model_dump(mode="json"),
        headers={"Content-Type": "application/problem+json"},
    )


def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    client_ip = request.client.host if request.client else "unknown"

    logger.exception(
        "An unhandled error occurred while processing the HTTP request.",
        extra={
            "http_status": 500,
            "error_msg": str(exc),
            "error_code": "INTERNAL_ERROR",
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown"),
        },
    )

    details = ProblemDetails(
        title="Internal Server Error",
        status=500,
        detail="An error occurred. Please try again later",
        code="INTERNAL_ERROR",
    )

    return JSONResponse(
        status_code=500,
        content=details.model_dump(mode="json"),
        headers={"Content-Type": "application/problem+json"},
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppError, app_exception_handler)  # type: ignore
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, global_exception_handler)  # type: ignore
