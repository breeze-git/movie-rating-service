from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .reviews import ReviewDTO


class UserBaseSchema(BaseModel):
    username: str


class UserGetResponse(UserBaseSchema):
    id: UUID
    reviews: list[ReviewDTO]

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserGetResponse):
    first_name: str | None
    last_name: str | None
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserPutRequest(UserBaseSchema):
    first_name: str | None
    last_name: str | None


class UserPatchRequest(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserUpdateResponse(BaseModel):
    message: str = "User's profile has been successfully updated"


class UserDeleteResponse(BaseModel):
    message: str = "User deleted"
