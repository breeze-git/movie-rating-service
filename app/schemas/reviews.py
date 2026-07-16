from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReviewPayload(BaseModel):
    message: str
    rating: int | None


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


class ReviewUpdate(BaseModel):
    message: str | None = None
    rating: int | None = None
