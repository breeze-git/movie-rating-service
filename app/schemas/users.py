from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .reviews import ReviewDetail


class UserBase(BaseModel):
    username: str


class UserBrief(UserBase):
    id: UUID
    first_name: str | None
    last_name: str | None
    email: str


class UserWithReviews(UserBase):
    id: UUID
    reviews: list[ReviewDetail]

    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserWithReviews):
    first_name: str | None
    last_name: str | None
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
