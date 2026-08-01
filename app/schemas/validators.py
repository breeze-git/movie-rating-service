import re
from collections.abc import Callable
from datetime import date
from typing import Annotated

from pydantic import AfterValidator


def _check_no_strip_empty(value: str) -> str:
    cleaned = value.strip()

    if not cleaned:
        raise ValueError("The value must not consist solely of whitespace")

    return cleaned


def _validate_password(password: str) -> str:
    PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[_!@#$%^&*(),.?":{}|<>])')

    if not PASSWORD_REGEX.match(password):
        raise ValueError(
            "The password must contain at least one uppercase letter, one lowercase letter,  one digit, and one special character."
        )

    return password


def _validate_age_limit(min_age: int) -> Callable:
    def inner(dob: date) -> date:
        today = date.today()

        cur_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if cur_age < min_age:
            raise ValueError(f"A person must be over {min_age} years old")

        return dob

    return inner


def _validate_release_year(release_year: int) -> int:
    year = date.today().year

    if release_year > year:
        raise ValueError("The year must be prior to the current year.")

    return release_year


NonEmptyString = Annotated[str, AfterValidator(_check_no_strip_empty)]
ValidPassword = Annotated[str, AfterValidator(_validate_password)]
YearEarlierThanCurrent = Annotated[int, AfterValidator(_validate_release_year)]
Over7YearsOld = Annotated[date, AfterValidator(_validate_age_limit(7))]
