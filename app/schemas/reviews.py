from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReviewCreateRequest(BaseModel):
    message: str
    rating: int | None


class ReviewDTO(BaseModel):
    id: UUID
    user_id: UUID
    movie_id: UUID
    message: str
    created_at: datetime
    updated_at: datetime | None = None
    rating: int | None

    model_config = ConfigDict(from_attributes=True)


class PaginatedReviewDTO(BaseModel):
    items: list[ReviewDTO]
    total: int
    limit: int | None = None
    offset: int | None = None


class ReviewSortBy(str, Enum):
    CREATION_DATE = "created_at"
    UPDATE_DATE = "updated_at"
    RATING = "rating"


class ReviewSort(BaseModel):
    sort_by: ReviewSortBy = ReviewSortBy.CREATION_DATE
    sort_desc: bool = False


class ReviewCreateResponse(BaseModel):
    id: UUID
    message: str = "Your review successfully added"


class ReviewManageResponse(BaseModel):
    message: str = "The review has been succesfully changed"


class ReviewDeleteResponse(BaseModel):
    message: str = "The review successfully deleted"


class ReviewPatchRequest(BaseModel):
    message: str | None = None
    rating: int | None = None
