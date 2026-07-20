from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.errors import ProblemDetails, ValidationErrorItem

from .base import AppException
from .mapping import ErrorMapping


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    status_code = ErrorMapping.app.get(exc.base_code, 400)

    details = ProblemDetails(
        title=exc.title,
        status=status_code,
        detail=exc.public_msg,
        code=exc.code,
    )

    return JSONResponse(
        status_code=status_code,
        content=details.model_dump(),
        headers={"Content-Type": "application/problem+json"},
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = ProblemDetails(
        title="Unprocessable Entity",
        status=422,
        detail="Invalid data",
        code="VALIDATION_ERROR",
        invalid_params=[ValidationErrorItem.model_validate(error) for error in exc.errors()],
    )

    return JSONResponse(
        status_code=422,
        content=details.model_dump(),
        headers={"Content-Type": "application/problem+json"},
    )


def http_exception_handler(request: Request, exc: HTTPException):
    title, code = ErrorMapping.http.get(exc.status_code, ("HTTP Error", "HTTP_ERROR"))

    details = ProblemDetails(
        title=title,
        status=exc.status_code,
        detail=exc.detail,
        code=code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=details.model_dump(),
        headers={"Content-Type": "application/problem+json"},
    )


def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    details = ProblemDetails(
        title="Internal Server Error",
        status=500,
        detail="An error occurred. Please try again later",
        code="INTERNAL_ERROR",
    )

    return JSONResponse(
        status_code=500,
        content=details.model_dump(),
        headers={"Content-Type": "application/problem+json"},
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, global_exception_handler)  # type: ignore
