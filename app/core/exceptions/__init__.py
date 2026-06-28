from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .base import AppException
from .mapping import ERROR_MAPPING


async def global_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    error = ERROR_MAPPING.get(
        type(exc), {"status_code": 500, "detail": "Internal server error"}  # type: ignore
    )

    return JSONResponse(
        status_code=error["status_code"], content={"detail": error["detail"]}
    )


def register_exception_handler(app: FastAPI):
    app.add_exception_handler(AppException, global_exception_handler)  # type: ignore
