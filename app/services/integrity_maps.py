from app.core.exceptions.services import (
    AlreadyExistsError,
    InvalidDataError,
    NotFoundError,
)

from .error_details import (
    DirectorErrorDetails,
    MovieErrorDetails,
    ReviewErrorDetails,
    UserErrorDetails,
)

USER_INTEGRITY_MAP = {
    "users_username_key": lambda exc, dto: AlreadyExistsError(
        **UserErrorDetails.already_exists(username=dto["username"])
    ),
    "users_email_key": lambda exc, dto: AlreadyExistsError(**UserErrorDetails.already_exists(email=dto["email"])),
    "users_not_null": lambda exc, dto: InvalidDataError(**UserErrorDetails.invalid_data(exc.column)),
}

MOVIE_INTEGRITY_MAP = {
    "movies_director_id_fkey": lambda exc, dto: NotFoundError(**DirectorErrorDetails.not_found(dto["director_id"])),
    "uq_movie_title_year_director": lambda exc, dto: AlreadyExistsError(**MovieErrorDetails.already_exists()),
    "check_release_year": lambda exc, dto: InvalidDataError(**MovieErrorDetails.invalid_data("release_year")),
    "country_movies_country_id_fkey": lambda exc, dto: NotFoundError(**MovieErrorDetails.countries_not_found()),
    "country_movies_movie_id_fkey": lambda exc, dto: NotFoundError(**MovieErrorDetails.not_found(dto["id"])),
    "genre_movies_genre_id_fkey": lambda exc, dto: NotFoundError(**MovieErrorDetails.genres_not_found()),
    "genre_movies_movie_id_fkey": lambda exc, dto: NotFoundError(**MovieErrorDetails.not_found(dto["id"])),
    "movies_not_null": lambda exc, dto: InvalidDataError(**MovieErrorDetails.invalid_data(exc.column)),
}


REVIEW_INTEGRITY_MAP = {
    "uq_review_user_id_movie_id": lambda exc, dto: AlreadyExistsError(
        **ReviewErrorDetails.already_exists(user_id=dto["user_id"], movie_id=dto["movie_id"])
    ),
    "reviews_movie_id_fkey": lambda exc, dto: NotFoundError(**MovieErrorDetails.not_found(dto["movie_id"])),
    "reviews_user_id_fkey": lambda exc, dto: NotFoundError(**UserErrorDetails.not_found(dto["user_id"])),
    "reviews_not_null": lambda exc, dto: InvalidDataError(**ReviewErrorDetails.invalid_data(exc.column)),
}

DIRECTOR_INTEGRITY_MAP = {
    "uq_director_full_name_date_of_birth": lambda exc, dto: AlreadyExistsError(**DirectorErrorDetails.already_exists()),
    "check_min_director_age": lambda exc, dto: InvalidDataError(**DirectorErrorDetails.invalid_data("date_of_birth")),
    "directors_not_null": lambda exc, dto: InvalidDataError(**DirectorErrorDetails.invalid_data(exc.column)),
}
