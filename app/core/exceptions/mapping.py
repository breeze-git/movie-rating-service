from .services import (
    InvalidCredentialsError,
    ReviewNotFoundError,
    UserAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)

ERROR_MAPPING = {
    InvalidCredentialsError: {
        "status_code": 401,
        "detail": "Authentication failed",
    },
    UserNotFoundError: {
        "status_code": 401,
        "detail": "Authentication failed",
    },
    UserAlreadyExistsError: {
        "status_code": 409,
        "detail": "User already exists",
    },
    UsernameAlreadyExistsError: {
        "status_code": 409,
        "detail": "User with this username already exists",
    },
    ReviewNotFoundError: {
        "status_code": 404,
        "detail": "Content not found",
    },
}
