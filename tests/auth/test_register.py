import pytest
from fastapi import status
from httpx2 import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.database.models import User
from app.schemas.auth import UserRegister
from app.schemas.users import UserBrief
from app.services.users.exceptions import UserAlreadyExistsError
from tests.conftest import URLPaths
from tests.helpers import assert_error_response, assert_validation_error


async def test_register_success(
    api_client: AsyncClient,
    db_session: AsyncSession,
    register_payload: UserRegister,
    endp_urls: URLPaths,
) -> None:
    response = await api_client.post(endp_urls.register_user, json=register_payload.model_dump(mode="json"))

    assert response.status_code == status.HTTP_201_CREATED

    raw_json = response.json()["data"]

    assert "password" not in raw_json
    assert "hashed_password" not in raw_json

    user_response = UserBrief.model_validate(raw_json)

    assert user_response.username == register_payload.username
    assert user_response.email == register_payload.email

    db_session.expire_all()

    query = select(User).where(User.email == register_payload.email)

    created_user = await db_session.scalar(query)

    assert created_user is not None
    assert created_user.id == user_response.id
    assert created_user.username == register_payload.username

    assert created_user.hashed_password != register_payload.password
    assert verify_password(register_payload.password, created_user.hashed_password)


async def test_duplicate_email(
    api_client: AsyncClient,
    registered_user_payload: UserRegister,
    endp_urls: URLPaths,
) -> None:
    response = await api_client.post(
        endp_urls.register_user,
        json=registered_user_payload.model_dump(mode="json"),
    )

    assert_error_response(response, status.HTTP_409_CONFLICT, UserAlreadyExistsError.code)

    error_data = response.json()

    assert error_data["conflict_reason"] == "email"


@pytest.mark.parametrize(
    "invalid_field, invalid_value, expected_error_loc",
    [
        ("email", "not-an-email-address", "email"),
        ("password", "simplepassword", "password"),
        ("username", "", "username"),
    ],
)
async def test_register_invalid_payload_fails(
    api_client: AsyncClient,
    register_payload: UserRegister,
    invalid_field: str,
    invalid_value: str,
    expected_error_loc: str,
    endp_urls: URLPaths,
) -> None:
    payload_dict = register_payload.model_dump(mode="json")

    payload_dict[invalid_field] = invalid_value

    response = await api_client.post(endp_urls.register_user, json=payload_dict)

    assert_validation_error(response, expected_error_loc)
