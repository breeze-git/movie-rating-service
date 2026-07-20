import re

from sqlalchemy.exc import IntegrityError

from app.core.exceptions.repositories import (
    RepoCheckViolationError,
    RepoForeignKeyViolationError,
    RepoNotNullViolationError,
    RepoUniqueViolationError,
    RepoUnknowViolation,
)

# ERROR CODES

UQ_VIOLATION = "23505"
FK_VIOLATION = "23503"
CHECK_VIOLATION = "23514"
NOT_NULL_VIOLATION = "23502"

# ERROR REGEX

TABLE_REGEX = re.compile(r'(?:table|relation) "([^"]+)"')
FK_REGEX = re.compile(r'violates foreign key constraint "([^"]+)"')
UQ_REGEX = re.compile(r'violates unique constraint "([^"]+)"')
CHECK_REGEX = re.compile(r'violates check constraint "([^"]+)"')
NOT_NULL_COLUMN_REGEX = re.compile(r'null value in column "([^"]+)"')


def _extract(regex: re.Pattern, text: str) -> str:
    match = regex.search(text)
    return match.group(1) if match else "unknown"


def parse_integrity_error(exc: IntegrityError):
    if not exc.orig:
        raise RuntimeError("IntegrityError wrapping empty orig exception")

    error_msg = str(exc.orig)
    sqlstate = getattr(exc.orig, "sqlstate", None)

    if sqlstate == FK_VIOLATION:
        constraint = _extract(FK_REGEX, error_msg)
        table = _extract(TABLE_REGEX, error_msg)

        return RepoForeignKeyViolationError(internal_msg=error_msg, constraint=constraint, table=table)

    if sqlstate == UQ_VIOLATION:
        constraint = _extract(UQ_REGEX, error_msg)

        return RepoUniqueViolationError(internal_msg=error_msg, constraint=constraint)

    if sqlstate == CHECK_VIOLATION:
        constraint = _extract(FK_REGEX, error_msg)
        table = _extract(TABLE_REGEX, error_msg)

        return RepoCheckViolationError(internal_msg=error_msg, constraint=constraint, table=table)

    if sqlstate == NOT_NULL_VIOLATION:
        table = _extract(TABLE_REGEX, error_msg)
        column = _extract(NOT_NULL_COLUMN_REGEX, error_msg)

        return RepoNotNullViolationError(
            internal_msg=error_msg,
            constraint=f"{table}_{column}_not_null",
            table=table,
            column=column,
        )

    return RepoUnknowViolation(internal_msg=error_msg, constraint="unknown")
