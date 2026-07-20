from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.repositories import RepositoryException
from app.core.exceptions.services import NotFoundError
from app.database.models import Review
from app.database.repositories.movie import MovieRepository
from app.database.repositories.review import ReviewRepository
from app.database.session import get_session
from app.schemas.common import CollectionEnvelope, PaginationParams
from app.schemas.reviews import (
    ReviewDetail,
    ReviewPayload,
    ReviewSortCriteria,
    ReviewUpdate,
)
from app.services.base import BaseService
from app.services.integrity_maps import REVIEW_INTEGRITY_MAP

from .error_details import MovieErrorDetails, ReviewErrorDetails


class ReviewService(BaseService):
    _integrity_map = REVIEW_INTEGRITY_MAP

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.reviews = ReviewRepository(session)
        self.movies = MovieRepository(session)

        super().__init__(session)

    async def get_movie_reviews(
        self, movie_id: UUID, sort: ReviewSortCriteria, pagination: PaginationParams
    ) -> CollectionEnvelope[ReviewDetail]:
        review_collection = await self.reviews.get_movie_reviews(
            movie_id,
            **sort.model_dump(),
            **pagination.model_dump(),
        )

        if review_collection is None:
            raise NotFoundError(**MovieErrorDetails.not_found(id=movie_id)) from None

        return review_collection

    async def get_review_by_id(self, review_id: UUID) -> Review:
        db_review = await self.reviews.get_by_id(review_id)

        if db_review is None:
            raise NotFoundError(**ReviewErrorDetails.not_found(id=review_id)) from None

        return db_review

    async def create_review(self, movie_id: UUID, user_id: UUID, dto: ReviewPayload) -> ReviewDetail:
        db_review = Review(
            user_id=user_id,
            movie_id=movie_id,
            **dto.model_dump(),
        )

        try:
            await self.reviews.save(db_review)
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, user_id=user_id, movie_id=movie_id, **dto.model_dump()) from None

        await self.movies.update_rating(movie_id)

        await self.session.commit()

        review = ReviewDetail.model_validate(db_review)

        return review

    async def update_review(self, review_id: UUID, dto: ReviewUpdate) -> ReviewDetail:
        db_review = await self.reviews.get_by_id(review_id)

        if db_review is None:
            raise NotFoundError(**ReviewErrorDetails.not_found(id=review_id)) from None

        update_data = dto.model_dump(exclude_unset=True)

        try:
            await self.reviews.update(db_review, update_data)
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, review_id=review_id, **update_data) from None

        await self.movies.update_rating(db_review.movie_id)

        await self.session.commit()

        review = ReviewDetail.model_validate(db_review)

        return review

    async def remove_review(self, review_id: UUID) -> None:
        result = await self.reviews.delete(review_id)

        if not result.scalar():
            raise NotFoundError(**ReviewErrorDetails.not_found(id=review_id)) from None

        await self.session.commit()
