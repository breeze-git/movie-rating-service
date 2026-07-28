from app.core.exceptions.domain import AlreadyExistsError, NotFoundError


class DirectorNotFoundError(NotFoundError):
    title: str = "Director Not Found"
    detail: str = "The director was not found."
    code: str = "DIRECTOR_NOT_FOUND"


class DirectorAlreadyExistsError(AlreadyExistsError):
    title: str = "Director Already Exists"
    detail: str = "Director with the same name and date of birth already exists"
    code: str = "DIRECTOR_ALREADY_EXISTS"
