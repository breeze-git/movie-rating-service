from fastapi import status
from httpx2 import AsyncClient

from app.core.exceptions.http import InvalidTokenError
from app.schemas.auth import Tokens
from tests.conftest import URLPaths
from tests.helpers import assert_error_response


async def test_refresh_token_success(
    api_client: AsyncClient,
    user_tokens: Tokens,
    endp_urls: URLPaths,
) -> None:
    response = await api_client.post(endp_urls.refresh_token, json={"refresh_token": user_tokens.refresh_token})

    assert response.status_code == status.HTTP_200_OK

    raw_json = response.json()["data"]

    assert "access_token" in raw_json
    assert "refresh_token" in raw_json

    response_data = Tokens.model_validate(raw_json)

    assert response_data.token_type == "bearer"


async def test_invalid_refresh_token_fail(api_client: AsyncClient, endp_urls: URLPaths) -> None:
    response = await api_client.post(endp_urls.refresh_token, json={"refresh_token": "invalid_refresh_token"})

    assert_error_response(response, status.HTTP_401_UNAUTHORIZED, InvalidTokenError.code)
