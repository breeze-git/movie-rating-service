from pydantic import BaseModel, EmailStr, Field


class UserBaseAuth(BaseModel):
    password: str = Field(min_length=12)


class UserLogin(UserBaseAuth):
    email: EmailStr


class UserRegister(UserBaseAuth):
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
