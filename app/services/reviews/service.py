import logging
from uuid import UUID

from fastapi import Depends

from app.core.exceptions.repository import RepoUniqueViolationError
from app.database.models import Review
from app.database.uow import UnitOfWork
from app.schemas.common import CollectionEnvelope, PaginationParams
from app.schemas.reviews import (
    ReviewDetail,
    ReviewPayload,
    ReviewSortCriteria,
    ReviewUpdate,
)
from app.services.movies.exceptions import MovieNotFoundError
from app.services.reviews.exceptions import (
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
)
from app.services.users.exceptions import UserNotFoundError

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(self, uow: UnitOfWork = Depends()):
        self.uow = uow

    async def is_review_owner(self, user_id: UUID, review_id: UUID) -> bool:
        async with self.uow:
            existed = await self.uow.reviews.is_owner(user_id, review_id)

            return existed

    async def get_movie_reviews(
        self, movie_id: UUID, sort: ReviewSortCriteria, pagination: PaginationParams
    ) -> CollectionEnvelope[ReviewDetail]:
        async with self.uow:
            if not await self.uow.movies.exists_by_id(movie_id):
                raise MovieNotFoundError(movie_id) from None

            review_collection = await self.uow.reviews.get_movie_reviews(
                movie_id,
                **sort.model_dump(),
                **pagination.model_dump(),
            )

            return review_collection

    async def create_review(self, movie_id: UUID, user_id: UUID, dto: ReviewPayload) -> ReviewDetail:
        async with self.uow:
            if not await self.uow.users.exists_by_id(user_id):
                raise UserNotFoundError(search_by="id", value=user_id)

            if not await self.uow.movies.exists_by_id(movie_id):
                raise MovieNotFoundError(movie_id)

            db_review = Review(
                user_id=user_id,
                movie_id=movie_id,
                **dto.model_dump(),
            )

            try:
                await self.uow.reviews.save(db_review)
            except RepoUniqueViolationError as e:
                raise ReviewAlreadyExistsError(
                    conflict_value={"user_id": user_id, "movie_id": movie_id},
                ) from e

            await self.uow.movies.update_rating(movie_id)

            review = ReviewDetail.model_validate(db_review)

            logger.info(
                "Review created",
                extra={"id": review.id},
            )

            return review

    async def update_review(self, review_id: UUID, dto: ReviewUpdate) -> ReviewDetail:
        async with self.uow:
            db_review = await self.uow.reviews.get_by_id(review_id)

            if db_review is None:
                raise ReviewNotFoundError(search_value=review_id) from None

            update_data = dto.model_dump(exclude_unset=True)

            await self.uow.reviews.update(db_review, update_data)

            await self.uow.movies.update_rating(db_review.movie_id)

            review = ReviewDetail.model_validate(db_review)

            return review

    async def remove_review(self, review_id: UUID) -> None:
        async with self.uow:
            result = await self.uow.reviews.delete(review_id)

            if not result.scalar():
                raise ReviewNotFoundError(review_id) from None

            logger.info(
                "Review deleted",
                extra={"id": review_id},
            )
