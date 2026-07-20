from typing import Any

from pydantic import BaseModel, ConfigDict


class ValidationErrorItem(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str

    code: str

    invalid_params: list[ValidationErrorItem] | None = None


def errors_model(*status_codes: int | str) -> dict[int | str, dict[str, Any]]:
    return {code: {"model": ProblemDetails} for code in status_codes}
