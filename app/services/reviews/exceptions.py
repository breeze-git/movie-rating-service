from app.core.exceptions.domain import AlreadyExistsError, NotFoundError


class ReviewNotFoundError(NotFoundError):
    title: str = "Review Not Found"
    detail: str = "The review was not found."
    code: str = "REVIEW_NOT_FOUND"


class ReviewAlreadyExistsError(AlreadyExistsError):
    title: str = "Review Already Exists"
    detail: str = "User has already left a review for this movie."
    code: str = "REVIEW_ALREADY_EXISTS"
