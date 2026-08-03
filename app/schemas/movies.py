from collections.abc import Sequence
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.validators import NonEmptyString, ValidReleaseYear

from .common import DirectorBrief

# Support entities


class CountryBase(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GenreBase(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# Movie


class MovieBase(BaseModel):
    title: NonEmptyString = Field(max_length=50)
    release_year: ValidReleaseYear = Field(ge=1895)


class MoviePayload(MovieBase):
    director_id: UUID
    description: NonEmptyString = Field(min_length=10, max_length=3000)
    country_ids: Sequence[int] = Field(min_length=1, max_length=10)
    genre_ids: Sequence[int] = Field(min_length=1, max_length=10)


class MovieUpdate(BaseModel):
    title: NonEmptyString | None = Field(default=None, max_length=50)
    description: NonEmptyString | None = Field(default=None, max_length=3000)
    release_year: ValidReleaseYear | None = Field(default=None, ge=1895)

    director_id: UUID | None = Field(default=None, max_length=36)

    country_ids: Sequence[int] | None = Field(default=None, max_length=10)
    genre_ids: Sequence[int] | None = Field(default=None, max_length=10)


class MovieBrief(MovieBase):
    id: UUID
    rating: float | None
    director: DirectorBrief

    model_config = ConfigDict(from_attributes=True)


class MovieCollection(BaseModel):
    items: list[MovieBrief]
    total: int
    limit: int | None = None
    offset: int | None = None


class MovieDetail(MovieBase):
    id: UUID
    description: str
    rating: float | None
    director: DirectorBrief
    countries: list[CountryBase]
    genres: list[GenreBase]

    model_config = ConfigDict(from_attributes=True)


class MovieSortBy(str, Enum):
    RELEASE_YEAR = "release_year"
    RATING = "rating"
    TITLE = "title"


class MovieSortCriteria(BaseModel):
    sort_by: MovieSortBy = MovieSortBy.RELEASE_YEAR
    sort_desc: bool = False


class MovieFilterCriteria(BaseModel):
    search: str | None
    country_ids: Sequence[int] | None
    genre_ids: Sequence[int] | None
    director_ids: Sequence[UUID] | None
