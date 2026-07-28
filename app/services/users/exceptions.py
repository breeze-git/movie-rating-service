from typing import Literal
from uuid import UUID

from app.core.exceptions.domain import AlreadyExistsError, DomainError, NotFoundError


class UserNotFoundError(NotFoundError):
    title: str = "User Not Found"
    detail: str = "The user was not found."
    code: str = "USER_NOT_FOUND"

    def __init__(self, *, search_by: Literal["id", "email"], value: str | UUID | int):
        self.searhc_by = search_by
        self.search_value = value

        super().__init__(search_value=value)


class UserAlreadyExistsError(AlreadyExistsError):
    title: str = "User Already Exists"
    detail: str = "The user already exists."
    code: str = "USER_ALREADY_EXISTS"

    def __init__(self, *, conflict_reason: Literal["email", "username"], value: str):
        self.conflict_reason = conflict_reason
        self.conflict_value = value

        super().__init__(conflict_value=value)


class InvalidCredentialsError(DomainError):
    title: str = "Unauthorized"
    detail: str = "Invalid email or password."
    code: str = "INVALID_CREDENTIALS"

    def __init__(self, *, email: str):
        self.user_email = email

        super().__init__(user_email=email)
