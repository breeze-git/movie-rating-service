from app.core.exceptions.error_messages import (
    DirectorMessages,
    MovieMessages,
    ReviewMessages,
    UserMessages,
)
from app.core.exceptions.services import (
    AlreadyExistsError,
    InvalidDataError,
    NotFoundError,
)

USER_INTEGRITY_MAP = {
    "users_username_key": lambda exc, dto: AlreadyExistsError(
        detail=UserMessages.already_exists(username=dto["username"])
    ),
    "users_email_key": lambda exc, dto: AlreadyExistsError(detail=UserMessages.already_exists(email=dto["email"])),
}

MOVIE_INTEGRITY_MAP = {
    "movies_director_id_fkey": lambda exc, dto: NotFoundError(detail=DirectorMessages.not_found(dto["director_id"])),
    "uq_movie_title_year_director": lambda exc, dto: AlreadyExistsError(detail=MovieMessages.already_exists()),
    "check_release_year": lambda exc, dto: InvalidDataError(detail=MovieMessages.invalid_data(dto["release_year"])),
    "country_movies_country_id_fkey": lambda exc, dto: NotFoundError(detail=MovieMessages.countries_not_found()),
    "country_movies_movie_id_fkey": lambda exc, dto: NotFoundError(detail=MovieMessages.not_found(dto["id"])),
    "genre_movies_genre_id_fkey": lambda exc, dto: NotFoundError(detail=MovieMessages.genres_not_found()),
    "genre_movies_movie_id_fkey": lambda exc, dto: NotFoundError(detail=MovieMessages.not_found(dto["id"])),
}

REVIEW_INTEGRITY_MAP = {
    "uq_review_user_id_movie_id": lambda exc, dto: AlreadyExistsError(detail=ReviewMessages.already_exists()),
    "reviews_movie_id_fkey": lambda exc, dto: NotFoundError(detail=MovieMessages.not_found(dto["movie_id"])),
    "reviews_user_id_fkey": lambda exc, dto: NotFoundError(detail=UserMessages.not_found(dto["user_id"])),
}

DIRECTOR_INTEGRITY_MAP = {
    "uq_director_full_name_date_of_birth": lambda exc, dto: AlreadyExistsError(
        detail=DirectorMessages.already_exists()
    ),
    "check_min_director_age": lambda exc, dto: InvalidDataError(
        detail=DirectorMessages.invalid_data(dto["date_of_birth"])
    ),
}
