from datetime import UTC, datetime
from uuid import UUID, uuid4

import asyncpg

from app.core.exceptions import ReviewNotFoundError, UserNotFoundError
from app.database.repositories import add_review_to_db, get_user_from_db_by_id
from app.schemas.reviews import UserFeedback


async def create_review(
    user_id: str, feedback: UserFeedback, session: asyncpg.Connection
) -> UUID:
    review_id = uuid4()

    user_data = await get_user_from_db_by_id(user_id, session)

    if not user_data:
        raise UserNotFoundError

    review = {
        "id": review_id,
        "user_id": user_id,
        "message": feedback.review,
        "created_on": datetime.now(UTC),
    }

    await add_review_to_db(review, session)

    return review_id


async def change_review(
    review_id: str, feedback: UserFeedback, session: asyncpg.Connection
) -> None:
    result = await session.fetchrow(
        """
        UPDATE reviews
        SET message = $2, 
            updated_at = $3
        WHERE id = $1
        RETURNING id;
    """,
        review_id,
        feedback.review,
        datetime.now(UTC),
    )

    if result is None:
        raise ReviewNotFoundError


async def remove_review(review_id: str, session: asyncpg.Connection) -> None:
    result = await session.fetchrow(
        """
        DELETE FROM reviews 
        WHERE id = $1
        RETURNING id
    """,
        review_id,
    )

    if result is None:
        raise ReviewNotFoundError
