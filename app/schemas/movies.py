from collections.abc import Sequence
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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
    title: str
    release_year: int


class MoviePayload(MovieBase):
    director_id: UUID
    description: str
    country_ids: list[int]
    genre_ids: list[int]


class MovieUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    release_year: int | None = None
    director_id: UUID | None = None

    country_ids: Sequence[int] | None = None
    genre_ids: Sequence[int] | None = None


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
    country_ids: Sequence[int] | None
    genre_ids: Sequence[int] | None
    director_ids: Sequence[UUID] | None
