from uuid import UUID


class MovieMessages:
    @staticmethod
    def not_found(movie_id: str | UUID):
        return f"Movie with id '{movie_id}' not found"

    @staticmethod
    def already_exists():
        return "Movie with the same title, release year and director already exists"

    @staticmethod
    def genres_not_found():
        return "One or more of the specified genres could not be found"

    @staticmethod
    def countries_not_found():
        return "One or more of the specified countries could not be found"

    @staticmethod
    def invalid_data(field: str):
        return f"Invalid {field} value"


class ReviewMessages:
    @staticmethod
    def not_found(review_id: str | UUID):
        return f"Review with id '{review_id}' not found"

    @staticmethod
    def already_exists():
        return "User has already reviewed this movie"


class DirectorMessages:
    @staticmethod
    def not_found(director_id: str | UUID):
        return f"Director with id '{director_id}' not found"

    @staticmethod
    def already_exists():
        return "Director with the same name and date of birth already exists"

    @staticmethod
    def invalid_data(field: str):
        return f"Invalid {field} value"


class UserMessages:
    @staticmethod
    def not_found(user_id: str | UUID | None = None, email: str | None = None):
        if email is not None:
            value = f"email '{email}'"
        elif user_id is not None:
            value = f"id '{user_id}'"
        else:
            raise ValueError("Either 'id' or 'email' must be provided.")

        return f"User with {value} not found"

    @staticmethod
    def already_exists(email: str | None = None, username: str | None = None):
        if email is not None:
            value = f"email '{email}'"
        elif username is not None:
            value = f"username '{username}'"
        else:
            raise ValueError("Either 'email' or 'username' must be provided.")

        return f"User with {value} already exists"
