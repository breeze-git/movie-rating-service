from uuid import UUID

from .base import AppError


class APIError(AppError):
    status_code: int


class RateLimitExceededError(APIError):
    title: str = "Too Many Requests"
    detail: str = "Rate limit exceeded."
    code: str = "RATE_LIMIT_EXCEEDED"
    status_code: int = 429

    def __init__(self, *, limit: str, user_identifier: str | UUID, retry_after: int):
        self.limit = limit
        self.user_identifier = user_identifier
        self.retry_after = retry_after  # как добавить заголовок в ответ?

        super().__init__(
            limit=limit,
            user_identifier=user_identifier,
            retry_after=retry_after,
        )


class NotEnoughRightsError(APIError):
    title: str = "Access Denied"
    detail: str = "You do not have the required permissions to perform this action."
    code: str = "INSUFFICIENT_PERMISSIONS"
    status_code: int = 403

    def __init__(
        self,
        *,
        user_id: str | UUID,
        user_permissions: list[str],
        required_scopes: list[str],
    ):
        super().__init__(
            user_id=user_id,
            user_permissions=user_permissions,
            required_scopes=required_scopes,
        )


class InvalidTokenError(APIError):
    title: str = "Invalid Access Token"
    detail: str = "The provided access token is malformed or invalid."
    code: str = "INVALID_TOKEN"
    status_code: int = 401

    def __init__(self, *, token: str):
        super().__init__(token=token)


class InvalidTokenClaimsError(APIError):
    title: str = "Invalid Token Payload"
    detail: str = "The token is cryptographically valid, but contains invalid or missing claims."
    code: str = "INVALID_TOKEN_CLAIMS"
    status_code: int = 400

    def __init__(self, *, user_id: str | None, token_type: str | None, req_token_type: str):
        super().__init__(
            user_id=user_id,
            token_type=token_type,
            req_token_type=req_token_type,
        )


class SessionExpiredError(APIError):
    title: str = "Session Expired"
    detail: str = "Your session has expired. Please refresh your token or log in again."
    code: str = "SESSION_EXPIRED"
    status_code: int = 401

    def __init__(self, *, token: str):
        super().__init__(token=token)
