from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import RowMapping, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.database.models import Movie, Review
from app.schemas.reviews import ReviewSortBy

from .pg_error_codes import PostgresErrorCode as pg_err


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_movie_reviews(
        self,
        id: UUID,
        sort_by: ReviewSortBy = ReviewSortBy.CREATION_DATE,
        sort_desc: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[Sequence[RowMapping], int]:
        movie = await self.session.get(Movie, id)

        if movie is None:
            raise EntityNotFoundError from None

        query = select(
            Review.id,
            Review.user_id,
            Review.movie_id,
            Review.message,
            Review.created_at,
            Review.updated_at,
            Review.rating,
        ).where(Review.movie_id == id)

        sort_column = getattr(Review, sort_by.value)

        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)

        reviews = result.mappings().all()

        return reviews, total

    async def get_by_id(self, id: UUID) -> Review | None:
        review = await self.session.get(Review, id)

        return review

    async def save(self, review: Review) -> None:
        self.session.add(review)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.FOREIGN_KEY_VIOLATION:
                raise EntityNotFoundError from None
            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def update(self, review: Review, review_data_dict: dict) -> None:
        for key, value in review_data_dict.items():
            setattr(review, key, value)

        review.updated_at = datetime.now()

    async def delete(self, review_id: UUID) -> None:
        stmt = delete(Review).where(Review.id == review_id)

        result = await self.session.execute(stmt)

        if not result.rowcount:  # type: ignore
            raise EntityNotFoundError from None
