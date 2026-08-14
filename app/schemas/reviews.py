from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.validators import NonEmptyString


class ReviewPayload(BaseModel):
    message: NonEmptyString = Field(min_length=10, max_length=400)
    rating: int | None = Field(ge=1, le=10)


class ReviewUpdate(BaseModel):
    message: NonEmptyString | None = Field(default=None, min_length=10, max_length=400)
    rating: int | None = Field(default=None, ge=1, le=10)


class ReviewDetail(BaseModel):
    id: UUID
    user_id: UUID
    movie_id: UUID
    message: str
    created_at: datetime
    updated_at: datetime | None = None
    rating: int | None

    model_config = ConfigDict(from_attributes=True)


class ReviewSortBy(str, Enum):
    CREATION_DATE = "created_at"
    UPDATE_DATE = "updated_at"
    RATING = "rating"


class ReviewSortCriteria(BaseModel):
    sort_by: ReviewSortBy = ReviewSortBy.CREATION_DATE
    sort_desc: bool = False
