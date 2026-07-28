from typing import Any

from app.schemas.errors import (
    AlreadyExistsProblemDetails,
    NotFoundProblemDetails,
    ProblemDetails,
    RateLimitExceededProblemDetails,
    ValidationErrorProblemDetails,
)


def errors_model(*status_codes: int) -> dict[int | str, dict[str, Any]]:
    models = {
        409: AlreadyExistsProblemDetails,
        404: NotFoundProblemDetails,
        422: ValidationErrorProblemDetails,
        429: RateLimitExceededProblemDetails,
    }

    return {code: {"model": models.get(code, ProblemDetails)} for code in status_codes}
