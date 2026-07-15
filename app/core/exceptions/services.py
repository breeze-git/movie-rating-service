from .base import AppException


class ServiceException(AppException):
    pass


class NotFoundError(ServiceException):
    pass


class AlreadyExistsError(ServiceException):
    pass


class InvalidCredentialsError(ServiceException):
    pass


class InvalidDataError(ServiceException):
    pass


class UnexpectedServiceError(ServiceException):
    pass
