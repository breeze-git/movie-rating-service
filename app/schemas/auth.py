from pydantic import BaseModel, EmailStr, Field


class UserBaseAuth(BaseModel):
    password: str = Field(min_length=12)


class UserLoginRequest(UserBaseAuth):
    email: EmailStr


class UserRegisterRequest(UserBaseAuth):
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None


class UserRegisterResponse(BaseModel):
    message: str = "New user registered"


class Token(BaseModel):
    refresh_token: str


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
