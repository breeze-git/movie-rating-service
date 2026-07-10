from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, RootModel


class DirectorBaseSchema(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date


class DirectorShortSchema(DirectorBaseSchema):
    id: UUID


class DirectorsSearchResponse(RootModel[list[DirectorShortSchema]]):
    model_config = ConfigDict(from_attributes=True)


class MovieShortSchema(BaseModel):
    id: UUID
    title: str
    release_year: int

    model_config = ConfigDict(from_attributes=True)


class DirectorGetResponse(DirectorBaseSchema):
    id: UUID
    movies: list[MovieShortSchema]

    model_config = ConfigDict(from_attributes=True)


class DirectorAddRequest(DirectorBaseSchema):
    pass


class DirectorAddResponse(BaseModel):
    id: UUID
    message: str = "Director is successfully added"


class DirectorManageResponse(BaseModel):
    message: str = "Director is successfully managed"


class DirectorPatchRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None


class DirectorDeleteResponse(BaseModel):
    message: str = "Director is successfully removed"
