from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.repositories as repo
from app.core.exceptions.services import ReviewNotFoundError, UserNotFoundError
from app.database.models import Review
from app.database.session import get_session
from app.schemas.reviews import ReviewCreateRequest


class ReviewService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def create_review(
        self, user_id: str, review_data: ReviewCreateRequest
    ) -> UUID:
        id = uuid4()

        user = await repo.get_user_by_id(self.session, user_id)

        if user is None:
            raise UserNotFoundError

        new_review = Review(
            id=id,
            user_id=user_id,
            message=review_data.message,
        )

        await repo.save_review(self.session, new_review)

        return id

    async def manage_review(
        self, review_id: str, review_data: ReviewCreateRequest
    ) -> None:
        review = await repo.get_review_by_id(self.session, review_id)

        if review is None:
            raise ReviewNotFoundError

        await repo.manage_review(self.session, review, review_data.message)

    async def remove_review(self, review_id: str) -> None:
        review = await repo.get_review_by_id(self.session, review_id)

        if review is None:
            raise ReviewNotFoundError

        await repo.remove_review(self.session, review)

    async def get_review_by_id(self, review_id: str) -> Review:
        review = await repo.get_review_by_id(self.session, review_id)

        if review is None:
            raise ReviewNotFoundError

        return review
