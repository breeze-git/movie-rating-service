from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select

from app.database.models import Movie, Review
from app.schemas.common import CollectionEnvelope
from app.schemas.reviews import ReviewDTO, ReviewSortBy

from .base import BaseRepository


class ReviewRepository(BaseRepository):
    model = Review

    async def get_movie_reviews(
        self,
        id: UUID,
        sort_by: ReviewSortBy = ReviewSortBy.CREATION_DATE,
        sort_desc: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> CollectionEnvelope | None:
        movie = await self.session.get(Movie, id)

        if movie is None:
            return

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

        rows = result.mappings().all()

        reviews = [ReviewDTO.model_validate(row) for row in rows]

        collection = CollectionEnvelope(
            items=reviews,
            total=total,
        )

        return collection

    async def update(self, review: Review, review_data_dict: dict) -> None:
        for key, value in review_data_dict.items():
            setattr(review, key, value)

        review.updated_at = datetime.now()

        await self._flush()
