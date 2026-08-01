from app.core.exceptions.domain import AlreadyExistsError, AppError, NotFoundError
from app.core.exceptions.http import APIError, RateLimitExceededError
from app.schemas.errors import (
    AlreadyExistsProblemDetails,
    NotFoundProblemDetails,
    ProblemDetails,
    RateLimitExceededProblemDetails,
)
from app.services.users.exceptions import InvalidCredentialsError


class ErrorMapping:
    @staticmethod
    def get_status_code_and_schema(exc: AppError):
        status_code = exc.status_code if isinstance(exc, APIError) else 400
        schema = ProblemDetails

        if isinstance(exc, NotFoundError):
            status_code, schema = 404, NotFoundProblemDetails
        elif isinstance(exc, AlreadyExistsError):
            status_code, schema = 409, AlreadyExistsProblemDetails
        elif isinstance(exc, InvalidCredentialsError):
            status_code, schema = 401, ProblemDetails
        elif isinstance(exc, RateLimitExceededError):
            status_code, schema = exc.status_code, RateLimitExceededProblemDetails

        return status_code, schema
