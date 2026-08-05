import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.auth import Tokens, UserRegister
from app.services.users.exceptions import InvalidCredentialsError
from tests.helpers import assert_error_response
from tests.urls import urls


async def test_login_success(
    api_client: AsyncClient,
    registered_user_payload: UserRegister,
) -> None:
    login_data = {
        "username": registered_user_payload.email,
        "password": registered_user_payload.password,
    }

    response = await api_client.post(urls.login_user, data=login_data)

    assert response.status_code == status.HTTP_200_OK

    raw_json = response.json()["data"]

    assert "access_token" in raw_json
    assert "refresh_token" in raw_json

    response_data = Tokens.model_validate(raw_json)

    assert response_data.token_type == "bearer"


@pytest.mark.parametrize(
    "credentials_override",
    [
        {"username": "unknown_user_email@test.com"},
        {"password": "invalid_password_123"},
    ],
    ids=["email", "password"],
)
async def test_login_invalid_credentials_fails(
    api_client: AsyncClient,
    registered_user_payload: UserRegister,
    credentials_override: dict,
) -> None:
    login_data = {
        "username": registered_user_payload.email,
        "password": registered_user_payload.password,
    }

    login_data.update(credentials_override)

    response = await api_client.post(urls.login_user, data=login_data)

    assert_error_response(response, status.HTTP_401_UNAUTHORIZED, InvalidCredentialsError.code)
