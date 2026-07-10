from .services import AlreadyExistsError, InvalidCredentialsError, NotFoundError

ERROR_MAPPING = {
    InvalidCredentialsError: {
        "status_code": 401,
        "detail": "Authentication failed",
    },
    NotFoundError: {
        "status_code": 404,
        "detail": "Requested resource was not found",
    },
    AlreadyExistsError: {"status_code": 409, "detail": "Resource already exists"},
}
