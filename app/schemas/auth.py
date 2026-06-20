from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)


class CreateUser(LoginUser):
    username: str
    first_name: str | None = None
    last_name: str | None = None


class UserToken(BaseModel):
    refresh_token: str


class TokensResp(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class CreateUserResp(BaseModel):
    message: str = "New user created"


class UserInDB(BaseModel):
    id: UUID
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str
    hashed_password: str
