from uuid import UUID

from pydantic import BaseModel


class CreateReview(BaseModel):
    id: UUID
    user_id: str
    message: str


class UserFeedback(BaseModel):
    review: str


class ReviewsResp(BaseModel):
    reviews: list


class CreateReviewResp(BaseModel):
    id: UUID
    message: str = "Your review successfully added"


class ManageReviewResp(BaseModel):
    message: str = "The review has been succesfully changed"


class DeleteReviewResp(BaseModel):
    message: str = "The review successfully deleted"
