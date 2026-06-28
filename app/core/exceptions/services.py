from .base import AppException


class ServiceException(AppException):
    pass


class UserNotFoundError(ServiceException):
    pass


class InvalidCredentialsError(ServiceException):
    pass


class UserAlreadyExistsError(ServiceException):
    pass


class ReviewNotFoundError(ServiceException):
    pass


class UsernameAlreadyExistsError(ServiceException):
    pass
