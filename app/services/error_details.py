from uuid import UUID


class BaseErrorDetails:
    entity: str

    @classmethod
    def not_found(cls, id: str | UUID):
        msg = f"{cls.entity} with id '{id}' not found"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": f"{cls.entity.upper()}_NOT_FOUND",
        }

    @classmethod
    def invalid_data(cls, field: str):
        msg = f"Invalid {cls.entity.lower()} {field} value"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": f"{cls.entity.upper()}_INVALID_DATA",
        }


class MovieErrorDetails(BaseErrorDetails):
    entity = "Movie"

    @staticmethod
    def already_exists():
        msg = "Movie with the same title, release year and director already exists"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": "MOVIE_ALREADY_EXISTS",
        }

    @staticmethod
    def genres_not_found():
        msg = "One or more of the specified genres could not be found"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": "GENRE_NOT_FOUND",
        }

    @staticmethod
    def countries_not_found():
        msg = "One or more of the specified countries could not be found"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": "COUNTRY_NOT_FOUND",
        }


class ReviewErrorDetails(BaseErrorDetails):
    entity = "Review"

    @staticmethod
    def already_exists(user_id: UUID | str, movie_id: UUID | str):
        return {
            "internal_msg": f"User with id '{user_id}' has already reviewed movie with id '{movie_id}'",
            "public_msg": "User has already reviewed this movie",
            "code": "REVIEW_ALREADY_EXISTS",
        }


class DirectorErrorDetails(BaseErrorDetails):
    entity = "Director"

    @staticmethod
    def already_exists():
        msg = "Director with the same name and date of birth already exists"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": "DIRECTOR_ALREADY_EXISTS",
        }


class UserErrorDetails(BaseErrorDetails):
    @staticmethod
    def not_found_by_email(email: str):
        msg = f"User with {email} not found"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": "USER_NOT_FOUND",
        }

    @staticmethod
    def already_exists(email: str | None = None, username: str | None = None):
        if email is not None:
            value = f"email '{email}'"
        elif username is not None:
            value = f"username '{username}'"
        else:
            raise ValueError("Either 'email' or 'username' must be provided.")

        msg = f"User with {value} already exists"

        return {
            "internal_msg": msg,
            "public_msg": msg,
            "code": "USER_ALREADY_EXISTS",
        }

    @staticmethod
    def invalid_credentials(email: str, pass_mismatch: bool = False):
        internal_msg = f"Invalid email '{email}'"

        if pass_mismatch:
            internal_msg = f"Password mismatch for user with email '{email}'. Submited hash didn't match."

        return {
            "internal_msg": internal_msg,
            "public_msg": "Invalid email or password",
            "code": "INVALID_CREDENTIALS",
        }
