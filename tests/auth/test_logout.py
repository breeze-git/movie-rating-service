from fastapi import status
from httpx import AsyncClient

from app.core.exceptions.http import InvalidTokenError, SessionExpiredError
from app.schemas.auth import Tokens
from tests.helpers import assert_error_response
from tests.urls import urls


async def test_logout_user_success(
    api_client: AsyncClient,
    user_tokens: Tokens,
) -> None:
    response = await api_client.post(urls.logout_user, json={"refresh_token": user_tokens.refresh_token})

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_invalid_refresh_token_fail(api_client: AsyncClient) -> None:
    response = await api_client.post(urls.logout_user, json={"refresh_token": "invalid_refresh_token"})

    assert_error_response(response, status.HTTP_401_UNAUTHORIZED, InvalidTokenError.code)


async def test_expired_user_session_fail(
    api_client: AsyncClient,
    user_tokens: Tokens,
) -> None:
    success_logout = await api_client.post(urls.logout_user, json={"refresh_token": user_tokens.refresh_token})

    assert success_logout.status_code == status.HTTP_204_NO_CONTENT

    error_response = await api_client.post(urls.logout_user, json={"refresh_token": user_tokens.refresh_token})

    assert_error_response(error_response, status.HTTP_401_UNAUTHORIZED, SessionExpiredError.code)


async def test_expired_refresh_token_fail(
    api_client: AsyncClient,
    user_tokens: Tokens,
):
    success_logout = await api_client.post(urls.logout_user, json={"refresh_token": user_tokens.refresh_token})

    assert success_logout.status_code == status.HTTP_204_NO_CONTENT

    refresh_response = await api_client.post(urls.refresh_token, json={"refresh_token": user_tokens.refresh_token})

    assert_error_response(refresh_response, status.HTTP_401_UNAUTHORIZED, SessionExpiredError.code)
