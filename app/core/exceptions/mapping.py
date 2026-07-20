from .services import (
    AlreadyExistsError,
    InvalidCredentialsError,
    InvalidDataError,
    NotFoundError,
)


class ErrorMapping:
    app: dict[str, int] = {
        InvalidDataError.base_code: 400,
        InvalidCredentialsError.base_code: 401,
        NotFoundError.base_code: 404,
        AlreadyExistsError.base_code: 409,
    }

    http: dict[int, tuple[str, str]] = {
        401: ("Unauthorized", "UNAUTHORIZED"),
        403: ("Forbidden", "FORBIDDEN"),
        429: ("Rate Limit Exceeded", "RATE_LIMIT_EXCEEDED"),
    }
