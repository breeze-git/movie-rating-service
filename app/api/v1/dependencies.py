from collections.abc import Sequence
from secrets import compare_digest
from uuid import UUID

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from limits import parse, strategies
from limits.storage import MemoryStorage

from app.core.exceptions.http import (
    InvalidTokenClaimsError,
    InvalidTokenError,
    NotEnoughRightsError,
    RateLimitExceededError,
    SessionExpiredError,
)
from app.core.settings import settings
from app.services.reviews.service import ReviewService
from app.services.users.service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

storage = MemoryStorage()
moving_window = strategies.MovingWindowRateLimiter(storage)


async def get_current_user_claims(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token_safely(token)

    verify_claims(payload, req_token_type="access")

    return payload


def verify_claims(payload: dict, req_token_type: str):
    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is None or token_type != req_token_type:
        raise InvalidTokenClaimsError(
            user_id=user_id,
            token_type=token_type,
            req_token_type=req_token_type,
        ) from None


def get_user_id_from_token(payload: dict = Depends(get_current_user_claims)) -> UUID:
    user_id = payload["sub"]

    return user_id


async def verify_review_permissions(
    review_id: UUID,
    security_scopes: SecurityScopes,
    payload: dict = Depends(get_current_user_claims),
    user_service: UserService = Depends(),
    review_service: ReviewService = Depends(),
) -> UUID:
    user_id = payload["sub"]

    review = await review_service.get_review_by_id(review_id)

    if compare_digest(str(review.user_id), user_id):
        return user_id

    required_scopes = security_scopes.scopes
    user_permissions = await user_service.get_user_permissions(user_id)

    if not check_permissions(user_permissions, required_scopes):
        raise NotEnoughRightsError(
            user_id=user_id,
            user_permissions=list(user_permissions),
            required_scopes=required_scopes,
        ) from None

    return user_id


async def verify_global_permissions(
    security_scopes: SecurityScopes,
    payload: dict = Depends(get_current_user_claims),
    user_service: UserService = Depends(),
) -> UUID:
    user_id = UUID(payload["sub"])

    required_scopes = security_scopes.scopes
    user_permissions = await user_service.get_user_permissions(user_id)

    if not check_permissions(user_permissions, required_scopes):
        raise NotEnoughRightsError(
            user_id=user_id,
            user_permissions=list(user_permissions),
            required_scopes=required_scopes,
        ) from None

    return user_id


def check_permissions(user_permissions: Sequence[str], required_scopes: list) -> bool:
    for scope in required_scopes:
        if scope not in user_permissions:
            return False

    return True


def decode_token_safely(token: str):
    try:
        payload = get_token_payload(token)

        return payload
    except jwt.ExpiredSignatureError:
        raise SessionExpiredError(token=token) from None
    except jwt.InvalidTokenError:
        raise InvalidTokenError(token=token) from None


def get_token_payload(token: str) -> dict:
    payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)

    return payload


# LIMITERS


class RoleBasedLimiter:
    async def __call__(
        self,
        request: Request,
        payload: dict = Depends(get_current_user_claims),
        user_service: UserService = Depends(),
    ) -> None:
        if settings.mode == "TEST":
            return

        user_id = payload["sub"]
        user_roles = await user_service.get_user_roles(user_id)

        user_identifier = f"user:{user_id}"
        limit = "20/minute"

        if "admin" in user_roles:
            limit = "1000/minute"

        endpoint_name = request.url.path

        check_limit(user_identifier, endpoint_name, limit)


class IPBasedLimiter:
    def __init__(self, limit: str):
        self.limit: str = limit

    def __call__(self, request: Request):
        user_identifier = request.client.host  # type: ignore
        endpoint_name = request.url.path

        check_limit(user_identifier, endpoint_name, self.limit)


def check_limit(user_identifier: str, endpoint_name: str, limit: str) -> None:
    if settings.mode == "TEST":
        return

    limit_item = parse(limit)

    if not moving_window.hit(limit_item, user_identifier, endpoint_name):
        raise RateLimitExceededError(
            limit=limit,
            user_identifier=user_identifier,
            retry_after=limit_item.get_expiry(),
        ) from None
