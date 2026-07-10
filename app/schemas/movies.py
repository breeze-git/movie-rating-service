from collections.abc import Sequence
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, RootModel


class MovieBaseSchema(BaseModel):
    title: str
    description: str
    release_year: int
    director_id: UUID

    model_config = ConfigDict(from_attributes=True)


class MovieSortBy(str, Enum):
    RELEASE_YEAR = "release_year"
    RATING = "rating"
    TITLE = "title"


class MovieSort(BaseModel):
    sort_by: MovieSortBy = MovieSortBy.RELEASE_YEAR
    sort_desc: bool = False


class MovieFilter(BaseModel):
    countries: Sequence[int] | None
    genres: Sequence[int] | None
    directors: Sequence[UUID] | None


class MovieDTO(BaseModel):
    id: UUID
    title: str
    release_year: int
    rating: float | None
    director_id: UUID
    director_first_name: str
    director_last_name: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedMovieDTO(BaseModel):
    items: list[MovieDTO]
    total: int
    limit: int | None = None
    offset: int | None = None


class CountrySchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MovieGetResponse(MovieBaseSchema):
    id: UUID
    rating: float | None
    countries: list[CountrySchema]
    genres: list[GenreSchema]


class MovieAddRequest(MovieBaseSchema):
    countries: list[int]
    genres: list[int]


class MovieAddResponse(BaseModel):
    id: UUID
    message: str = "Movie is successfully added"


class MovieManageResponse(BaseModel):
    message: str = "Movie is successfully managed"


class MoviePatchRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    release_year: int | None = None
    director_id: UUID | None = None

    countries: list[int] | None = None
    genres: list[int] | None = None


class MovieDeleteResponse(BaseModel):
    message: str = "Movie is successfully deleted"


class GenresGetResponse(RootModel[list[GenreSchema]]):
    model_config = ConfigDict(from_attributes=True)


class CountriesGetResponse(RootModel[list[CountrySchema]]):
    model_config = ConfigDict(from_attributes=True)
