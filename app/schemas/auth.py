from pydantic import BaseModel, EmailStr, Field

from app.schemas.validators import NonEmptyString, ValidPassword


class UserBaseAuth(BaseModel):
    password: ValidPassword = Field(min_length=13, max_length=60)


class UserLogin(UserBaseAuth):
    email: EmailStr = Field(max_length=100)


class UserRegister(UserBaseAuth):
    username: NonEmptyString = Field(max_length=50)
    email: EmailStr = Field(max_length=100)
    first_name: NonEmptyString | None = Field(default=None, max_length=50)
    last_name: NonEmptyString | None = Field(default=None, max_length=50)


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
