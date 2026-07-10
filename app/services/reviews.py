from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.error_messages import MovieMessages, ReviewMessages
from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.core.exceptions.services import AlreadyExistsError, NotFoundError
from app.database.models import Review
from app.database.repositories.movie import MovieRepository
from app.database.repositories.review import ReviewRepository
from app.database.session import get_session
from app.schemas.pagination import PaginationParams
from app.schemas.reviews import (
    PaginatedReviewDTO,
    ReviewCreateRequest,
    ReviewDTO,
    ReviewPatchRequest,
    ReviewSort,
)


class ReviewService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.reviews = ReviewRepository(session)
        self.movies = MovieRepository(session)

    async def get_movie_reviews(
        self, movie_id: UUID, sort: ReviewSort, pagination: PaginationParams
    ) -> PaginatedReviewDTO:
        try:
            reviews, total = await self.reviews.get_movie_reviews(
                movie_id,
                **sort.model_dump(),
                **pagination.model_dump(),
            )
        except EntityNotFoundError:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        review_dtos = [ReviewDTO.model_validate(row) for row in reviews]

        return PaginatedReviewDTO(items=review_dtos, total=total)

    async def get_review_by_id(self, review_id: UUID) -> Review:
        review = await self.reviews.get_by_id(review_id)

        if review is None:
            raise NotFoundError(detail=ReviewMessages.not_found(review_id=review_id)) from None

        return review

    async def create_review(self, movie_id: UUID, user_id: UUID, review_data: ReviewCreateRequest) -> UUID:
        id = uuid4()

        new_review = Review(
            id=id,
            user_id=user_id,
            movie_id=movie_id,
            message=review_data.message,
            rating=review_data.rating,
        )

        try:
            await self.reviews.save(new_review)

        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=ReviewMessages.already_exists()) from None
        except EntityNotFoundError:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        await self.movies.update_rating(movie_id)

        await self.session.commit()

        return id

    async def update_review(self, review_id: UUID, review_data: ReviewCreateRequest) -> None:
        review = await self.reviews.get_by_id(review_id)

        if review is None:
            raise NotFoundError(detail=ReviewMessages.not_found(review_id=review_id)) from None

        review_data_dict = review_data.model_dump()

        await self.reviews.update(review, review_data_dict)

        await self.movies.update_rating(review.movie_id)

        await self.session.commit()

    async def partial_update_review(self, review_id: UUID, review_data: ReviewPatchRequest) -> None:
        review = await self.reviews.get_by_id(review_id)

        if review is None:
            raise NotFoundError(detail=ReviewMessages.not_found(review_id=review_id)) from None

        review_data_dict = review_data.model_dump(exclude_unset=True)

        await self.reviews.update(review, review_data_dict)

        await self.movies.update_rating(review.movie_id)

        await self.session.commit()

    async def remove_review(self, review_id: UUID) -> None:
        try:
            await self.reviews.delete(review_id)
        except EntityNotFoundError:
            raise NotFoundError(detail=ReviewMessages.not_found(review_id=review_id)) from None

        await self.session.commit()
