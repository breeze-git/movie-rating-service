from .base import AppException


class RepositoryException(AppException):
    pass


class EntityNotFoundError(RepositoryException):
    pass


class EntityAlreadyExistsError(RepositoryException):
    pass


class ForeignKeyConstraintError(RepositoryException):
    pass


class DBOperationalError(RepositoryException):
    pass
