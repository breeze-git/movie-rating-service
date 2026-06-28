from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBaseAuth(BaseModel):
    password: str = Field(min_length=12)


class UserLoginRequest(UserBaseAuth):
    email: EmailStr


class UserCreateRequest(UserBaseAuth):
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None


class Token(BaseModel):
    refresh_token: str


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserCreateResponse(BaseModel):
    message: str = "New user created"


class UserDeleteResponse(BaseModel):
    message: str = "User deleted"


class UserInDB(BaseModel):
    id: UUID
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str
    hashed_password: str
