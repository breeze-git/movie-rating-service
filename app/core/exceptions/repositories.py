import re

from sqlalchemy.exc import IntegrityError

from .base import AppException

# ERROR CODES

UQ_VIOLATION = "23505"
FK_VIOLATION = "23503"
CHECK_VIOLATION = "23514"

# ERROR REGEX

TABLE_REGEX = re.compile(r'table "([^"]+)"')  # relation?
FK_REGEX = re.compile(r'violates foreign key constraint "([^"]+)"')
UQ_REGEX = re.compile(r'violates unique constraint "([^"]+)"')
CHECK_REGEX = re.compile(r'violates check constraint "([^"]+)"')


class RepositoryException(AppException):
    def __init__(self, constraint: str, detail: str | None = None):
        self.constraint = constraint
        super().__init__(detail=detail or f"Database integrity violation {constraint}")


class RepoForeignKeyViolationError(RepositoryException):
    def __init__(self, constraint: str, table: str):
        self.constraint = constraint
        self.table = table
        super().__init__(
            constraint=constraint,
            detail=f"Database integrity violation {constraint} on table {table}",
        )


class RepoEntityNotFoundError(RepositoryException):
    pass


class RepoUniqueViolationError(RepositoryException):
    pass


class RepoCheckViolationError(RepositoryException):
    pass


def parse_integrity_error(exc: IntegrityError):
    if not exc.orig:
        return RepositoryException("unknown_constraint")

    error_msg = str(exc.orig)
    sqlstate = getattr(exc.orig, "sqlstate", None)

    if sqlstate == FK_VIOLATION:
        match_constraint = FK_REGEX.search(error_msg)
        constraint_name = match_constraint.group(1) if match_constraint else "unknown_fk_constraint"

        match_table = TABLE_REGEX.search(error_msg)
        table_name = match_table.group(1) if match_table else "unknown_table"

        return RepoForeignKeyViolationError(constraint=constraint_name, table=table_name)

    if sqlstate == UQ_VIOLATION:
        match = UQ_REGEX.search(error_msg)
        constraint_name = match.group(1) if match else "unknown_uq_constraint"

        return RepoUniqueViolationError(constraint=constraint_name)

    if sqlstate == CHECK_VIOLATION:
        match = CHECK_REGEX.search(error_msg)
        constraint_name = match.group(1) if match else "unknown_check_constraint"

        return RepoCheckViolationError(constraint=constraint_name)

    return RepositoryException(constraint="unknown_constraint")
