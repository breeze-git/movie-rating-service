from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.validators import NonEmptyString


class UserBase(BaseModel):
    username: str


class UserBrief(UserBase):
    id: UUID
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserBase):
    id: UUID
    first_name: str | None
    last_name: str | None
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: NonEmptyString | None = Field(default=None, max_length=50)
    first_name: NonEmptyString | None = Field(default=None, max_length=50)
    last_name: NonEmptyString | None = Field(default=None, max_length=50)
