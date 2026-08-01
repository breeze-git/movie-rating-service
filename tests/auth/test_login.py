import pytest
from fastapi import status
from httpx2 import AsyncClient

from app.schemas.auth import Tokens, UserRegister
from app.services.users.exceptions import InvalidCredentialsError
from tests.conftest import URLPaths


async def test_login_success(
    api_client: AsyncClient,
    registered_user: UserRegister,
    endp_urls: URLPaths,
) -> None:
    login_data = {
        "username": registered_user.email,
        "password": registered_user.password,
    }

    response = await api_client.post(endp_urls.login_user, data=login_data)

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
    ids=["unknown_email", "invalid_password"],
)
async def test_login_invalid_credentials_fails(
    api_client: AsyncClient,
    registered_user: UserRegister,
    credentials_override: dict,
    endp_urls: URLPaths,
) -> None:
    login_data = {
        "username": registered_user.email,
        "password": registered_user.password,
    }

    login_data.update(credentials_override)

    response = await api_client.post(endp_urls.login_user, data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    raw_json = response.json()

    assert raw_json["status"] == status.HTTP_401_UNAUTHORIZED
    assert raw_json["code"] == InvalidCredentialsError.code
