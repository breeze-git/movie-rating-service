from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int = 400
    detail: str

    code: str

    model_config = ConfigDict(from_attributes=True)


class NotFoundProblemDetails(ProblemDetails):
    status: int = 404
    search_by: str = "id"
    search_value: str | UUID | int

    model_config = ConfigDict(from_attributes=True)


class AlreadyExistsProblemDetails(ProblemDetails):
    status: int = 409
    conflict_reason: str = "composite_key"

    model_config = ConfigDict(from_attributes=True)


class RateLimitExceededProblemDetails(ProblemDetails):
    status: int = 429
    limit: str
    user_identifier: str | UUID
    retry_after: int

    model_config = ConfigDict(from_attributes=True)


class ValidationErrorItem(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class ValidationErrorProblemDetails(ProblemDetails):
    status: int = 422
    code: str = "VALIDATION_ERROR"

    invalid_params: list[ValidationErrorItem] | None = None

    model_config = ConfigDict(from_attributes=True)
