from .base import AppException


class ServiceException(AppException):
    pass


class NotFoundError(ServiceException):
    title: str = "Resource Not Found"
    public_msg: str = "Requested resource was not found"
    base_code: str = "RESOURCE_NOT_FOUND"


class AlreadyExistsError(ServiceException):
    title: str = "Conflict"
    public_msg: str = "Resource already exists"
    base_code: str = "RESOURCE_ALREADY_EXISTS"


class InvalidCredentialsError(ServiceException):
    title: str = "Unauthorized"
    public_msg: str = "Invalid email or password"
    base_code: str = "INVALID_CREDENTIALS"


class InvalidDataError(ServiceException):
    title: str = "Bad Request"
    public_msg: str = "Invalid data"
    base_code: str = "INVALID_DATA"


class UnexpectedServiceError(ServiceException):
    pass
