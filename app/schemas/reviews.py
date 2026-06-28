from datetime import datetime
from typing import Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReviewCreateRequest(BaseModel):
    message: str


class ReviewResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    message: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ReviewsGetResponse(BaseModel):
    reviews: Sequence[ReviewResponseSchema]


class ReviewCreateResponse(BaseModel):
    id: UUID
    message: str = "Your review successfully added"


class ReviewManageResponse(BaseModel):
    message: str = "The review has been succesfully changed"


class ReviewDeleteResponse(BaseModel):
    message: str = "The review successfully deleted"
