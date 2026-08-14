from collections.abc import Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import ColumnElement, Result, delete, exists, func, select

from app.database.models import Review
from app.schemas.common import CollectionEnvelope
from app.schemas.reviews import ReviewDetail, ReviewSortBy

from .base import BaseRepository


class ReviewRepository(BaseRepository):
    model = Review

    async def is_owner(self, user_id: UUID, review_id: UUID) -> bool:
        query = select(exists().where(Review.id == review_id, Review.user_id == user_id))

        result = await self.session.scalar(query)

        return bool(result)

    async def _get_reviews(
        self,
        condition: ColumnElement[bool],
        sort_by: ReviewSortBy,
        sort_desc: bool,
        limit: int,
        offset: int,
    ) -> CollectionEnvelope[ReviewDetail]:
        query = select(
            Review.id,
            Review.user_id,
            Review.movie_id,
            Review.message,
            Review.created_at,
            Review.updated_at,
            Review.rating,
        ).where(condition)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        sort_column = getattr(Review, sort_by.value)

        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)

        rows = result.mappings().all()

        reviews = [ReviewDetail.model_validate(row) for row in rows]

        collection = CollectionEnvelope(
            items=reviews,
            total=total,
            limit=limit,
            offset=offset,
        )

        return collection

    async def get_movie_reviews(
        self,
        movie_id: UUID,
        sort_by: ReviewSortBy = ReviewSortBy.CREATION_DATE,
        sort_desc: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> CollectionEnvelope[ReviewDetail]:
        condition = Review.movie_id == movie_id

        collection = await self._get_reviews(condition, sort_by, sort_desc, limit, offset)

        return collection

    async def get_user_reviews(
        self,
        user_id: UUID,
        sort_by: ReviewSortBy = ReviewSortBy.CREATION_DATE,
        sort_desc: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> CollectionEnvelope[ReviewDetail]:
        condition = Review.movie_id == user_id

        collection = await self._get_reviews(condition, sort_by, sort_desc, limit, offset)

        return collection

    async def update(self, review: Review, update_data: Mapping[str, Any]) -> None:
        for key, value in update_data.items():
            setattr(review, key, value)

        review.updated_at = datetime.now()

        await self._flush()

    async def delete(self, review_id) -> Result[Any]:
        stmt = delete(Review).where(Review.id == review_id).returning(Review.id, Review.movie_id)

        result = await self._execute(stmt)

        return result
