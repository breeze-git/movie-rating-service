from collections.abc import Callable

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.schemas.users import UserDetail, UserUpdate
from app.services.users.exceptions import UserAlreadyExistsError
from tests.factories.users import UserRegisterFactory, UserUpdateFactory
from tests.helpers import assert_error_response, assert_validation_error
from tests.urls import urls


async def test_update_user_success(
    user_client: AsyncClient,
    db_session: AsyncSession,
):
    update_payload = UserUpdate(first_name="Jack")

    response = await user_client.patch(
        urls.update_user,
        json=update_payload.model_dump(exclude_unset=True, mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK

    raw_json = response.json()["data"]

    assert "password" not in raw_json
    assert "hashed_password" not in raw_json

    response_data = UserDetail.model_validate(raw_json)

    query = select(User).where(User.id == response_data.id)

    db_user = await db_session.scalar(query)

    assert db_user is not None
    assert db_user.first_name == update_payload.first_name

    assert db_user.username is not None
    assert db_user.last_name is not None


async def test_update_user_duplicate_username_fail(
    user_client: AsyncClient,
    create_user_in_db: Callable,
):
    other_user_payload = UserRegisterFactory.build()
    await create_user_in_db(other_user_payload)

    update_payload = UserUpdate(username=other_user_payload.username)

    response = await user_client.patch(
        urls.update_user,
        json=update_payload.model_dump(exclude_unset=True, mode="json"),
    )

    assert_error_response(response, status.HTTP_409_CONFLICT, UserAlreadyExistsError.code)

    error_data = response.json()

    assert error_data["conflict_reason"] == "username"


@pytest.mark.parametrize(
    "invalid_field, invalid_value, expected_error_loc",
    [
        ("username", "", "username"),
        ("first_name", "", "first_name"),
        ("last_name", "", "last_name"),
    ],
    ids=["username", "first_name", "last_name"],
)
async def test_update_user_invalid_payload_fails(
    user_client: AsyncClient,
    invalid_field: str,
    invalid_value: str,
    expected_error_loc: str,
):
    payload_dict = UserUpdateFactory.build().model_dump(mode="json")
    payload_dict[invalid_field] = invalid_value

    response = await user_client.patch(urls.update_user, json=payload_dict)

    assert_validation_error(response, expected_error_loc)
