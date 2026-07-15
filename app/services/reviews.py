from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.error_messages import MovieMessages, ReviewMessages
from app.core.exceptions.repositories import RepositoryException
from app.core.exceptions.services import NotFoundError
from app.database.models import Review
from app.database.repositories.movie import MovieRepository
from app.database.repositories.review import ReviewRepository
from app.database.session import get_session
from app.schemas.common import CollectionEnvelope
from app.schemas.pagination import PaginationParams
from app.schemas.reviews import ReviewCreateRequest, ReviewPatchRequest, ReviewSort
from app.services.base import BaseService
from app.services.integrity_maps import REVIEW_INTEGRITY_MAP


class ReviewService(BaseService):
    _integrity_map = REVIEW_INTEGRITY_MAP

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.reviews = ReviewRepository(session)
        self.movies = MovieRepository(session)

        super().__init__(session)

    async def get_movie_reviews(
        self, movie_id: UUID, sort: ReviewSort, pagination: PaginationParams
    ) -> CollectionEnvelope:
        review_collection = await self.reviews.get_movie_reviews(
            movie_id,
            **sort.model_dump(),
            **pagination.model_dump(),
        )

        if review_collection is None:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        return review_collection

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
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, user_id=user_id, movie_id=movie_id) from None

        await self.movies.update_rating(movie_id)

        await self.session.commit()

        return id

    async def update_review(self, review_id: UUID, review_data: ReviewPatchRequest) -> None:
        review = await self.reviews.get_by_id(review_id)

        if review is None:
            raise NotFoundError(detail=ReviewMessages.not_found(review_id=review_id)) from None

        review_data_dict = review_data.model_dump(exclude_unset=True)

        try:
            await self.reviews.update(review, review_data_dict)
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, review_id=review_id) from None

        await self.movies.update_rating(review.movie_id)

        await self.session.commit()

    async def remove_review(self, review_id: UUID) -> None:
        result = await self.reviews.delete(review_id)

        if not result.scalar():
            raise NotFoundError(ReviewMessages.not_found(review_id=review_id)) from None

        await self.session.commit()
