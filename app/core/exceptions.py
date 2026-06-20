class ServiceException(Exception):
    pass


class UserNotFoundError(ServiceException):
    pass


class ReviewNotFoundError(ServiceException):
    pass


class UsernameAlredyExistsError(ServiceException):
    pass
