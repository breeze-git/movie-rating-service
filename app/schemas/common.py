from datetime import date
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T


class CollectionEnvelope(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int | None = None
    offset: int | None = None


class DirectorBrief(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    date_of_birth: date

    model_config = ConfigDict(from_attributes=True)


class MovieShort(BaseModel):
    id: UUID
    title: str
    release_year: int

    model_config = ConfigDict(from_attributes=True)
