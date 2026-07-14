from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .common import MovieShort


class DirectorBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date


class DirectorDetail(DirectorBase):
    id: UUID
    movies: list[MovieShort]

    model_config = ConfigDict(from_attributes=True)


class DirectorUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
