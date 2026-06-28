from secrets import compare_digest

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from limits import parse, strategies
from limits.storage import MemoryStorage

from app.core.settings import settings
from app.services.auth import UserService
from app.services.reviews import ReviewService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

storage = MemoryStorage()
moving_window = strategies.MovingWindowRateLimiter(storage)


def get_current_user_claims(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token_safely(token)

    return payload


async def verify_permissions(
    request: Request,
    security_scopes: SecurityScopes,
    payload: dict = Depends(get_current_user_claims),
    review_id: str | None = None,
    user_service: UserService = Depends(),
    review_service: ReviewService = Depends(),
) -> str:
    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None

    if review_id is not None:
        review = await review_service.get_review_by_id(review_id)

        if compare_digest(str(review.user_id), user_id):
            return user_id

    required_scopes = security_scopes.scopes

    user_permissions = await user_service.get_user_permissions(user_id)

    if not user_permissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None

    for scope in required_scopes:
        if scope not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough rights",
            ) from None

    return user_id


def decode_token_safely(token: str):
    try:
        payload = get_token_payload(token)

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None


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
    limit_item = parse(limit)

    if not moving_window.hit(limit_item, user_identifier, endpoint_name):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {limit}",
        ) from None
