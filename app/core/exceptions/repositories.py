from .base import AppException


class RepositoryException(AppException):
    def __init__(
        self,
        internal_msg: str,
        constraint: str,
        table: str | None = None,
        column: str | None = None,
    ):
        self.constraint = constraint
        self.table = table

        super().__init__(internal_msg=internal_msg)


class RepoForeignKeyViolationError(RepositoryException):
    pass


class RepoUniqueViolationError(RepositoryException):
    pass


class RepoCheckViolationError(RepositoryException):
    pass


class RepoNotNullViolationError(RepositoryException):
    pass


class RepoUnknowViolation(RepositoryException):
    pass
