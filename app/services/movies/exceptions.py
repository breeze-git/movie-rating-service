from app.core.exceptions.domain import AlreadyExistsError, NotFoundError


class MovieNotFoundError(NotFoundError):
    title: str = "Movie Not Found"
    detail: str = "The movie was not found."
    code: str = "MOVIE_NOT_FOUND"


class MovieAlreadyExistsError(AlreadyExistsError):
    title: str = "Movie Already Exists"
    detail: str = "Movie with the same title, release year and director already exists"
    code: str = "MOVIE_ALREADY_EXISTS"


class GenresNotFoundError(NotFoundError):
    title: str = "Genres Not Found"
    detail: str = "One or more of the specified genres could not be found"
    code: str = "GENRES_NOT_FOUND"


class CountriesNotFoundError(NotFoundError):
    title: str = "Countries Not Found"
    detail: str = "One or more of the specified countries could not be found"
    code: str = "COUNTRIES_NOT_FOUND"
