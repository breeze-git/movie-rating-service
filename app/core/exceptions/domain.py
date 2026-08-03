from collections.abc import Mapping, Sequence
from uuid import UUID

from .base import AppError


class DomainError(AppError):
    pass


class NotFoundError(DomainError):
    def __init__(self, search_value: str | UUID | int | Sequence[str | UUID | int]):
        self.search_value = search_value

        super().__init__(
            search_value=search_value,
        )


class AlreadyExistsError(DomainError):
    def __init__(self, *, conflict_value: str | Mapping[str, str | UUID | int]):
        self.conflict_value = conflict_value

        super().__init__(conflict_value=conflict_value)
