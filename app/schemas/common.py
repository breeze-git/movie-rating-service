from datetime import date
from typing import Generic, TypeVar
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T


class CollectionEnvelope(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int | None = None
    offset: int | None = None


class PaginationParams(BaseModel):
    limit: int = Query(default=10, ge=1, le=100)
    offset: int = Query(default=0, ge=0)


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
