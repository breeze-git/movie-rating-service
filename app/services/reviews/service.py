import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.repository import RepoUniqueViolationError
from app.database.models import Review
from app.database.repositories.movie import MovieRepository
from app.database.repositories.review import ReviewRepository
from app.database.repositories.user import UserRepository
from app.database.session import get_session
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
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

        self.reviews = ReviewRepository(session)
        self.movies = MovieRepository(session)
        self.users = UserRepository(session)

    async def get_movie_reviews(
        self, movie_id: UUID, sort: ReviewSortCriteria, pagination: PaginationParams
    ) -> CollectionEnvelope[ReviewDetail]:
        review_collection = await self.reviews.get_movie_reviews(
            movie_id,
            **sort.model_dump(),
            **pagination.model_dump(),
        )

        if review_collection is None:
            raise MovieNotFoundError(movie_id) from None

        return review_collection

    async def get_review_by_id(self, review_id: UUID) -> Review:
        db_review = await self.reviews.get_by_id(review_id)

        if db_review is None:
            raise ReviewNotFoundError(review_id) from None

        return db_review

    async def create_review(self, movie_id: UUID, user_id: UUID, dto: ReviewPayload) -> ReviewDetail:
        if not await self.users.exists_by_id(user_id):
            raise UserNotFoundError(search_by="id", value=user_id)

        if not await self.movies.exists_by_id(movie_id):
            raise MovieNotFoundError(movie_id)

        db_review = Review(
            user_id=user_id,
            movie_id=movie_id,
            **dto.model_dump(),
        )

        try:
            await self.reviews.save(db_review)
        except RepoUniqueViolationError as e:
            raise ReviewAlreadyExistsError(
                conflict_value={"user_id": user_id, "movie_id": movie_id},
            ) from e

        await self.movies.update_rating(movie_id)

        await self.session.commit()

        review = ReviewDetail.model_validate(db_review)

        logger.info(
            "Review created",
            extra={"id": review.id},
        )

        return review

    async def update_review(self, review_id: UUID, dto: ReviewUpdate) -> ReviewDetail:
        db_review = await self.reviews.get_by_id(review_id)

        if db_review is None:
            raise ReviewNotFoundError(search_value=review_id) from None

        update_data = dto.model_dump(exclude_unset=True)

        await self.reviews.update(db_review, update_data)

        await self.movies.update_rating(db_review.movie_id)

        await self.session.commit()

        review = ReviewDetail.model_validate(db_review)

        return review

    async def remove_review(self, review_id: UUID) -> None:
        result = await self.reviews.delete(review_id)

        if not result.scalar():
            raise ReviewNotFoundError(review_id) from None

        await self.session.commit()

        logger.info(
            "Review deleted",
            extra={"id": review_id},
        )
