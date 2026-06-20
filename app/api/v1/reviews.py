import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request, Security, status

from app.core.exceptions import ReviewNotFoundError, UserNotFoundError
from app.core.limiters import IPBasedLimiter, RoleBasedLimiter
from app.core.security import verify_permissions
from app.database.database import get_session
from app.database.repositories import get_reviews_from_db
from app.schemas.reviews import (
    CreateReviewResp,
    DeleteReviewResp,
    ManageReviewResp,
    ReviewsResp,
    UserFeedback,
)
from app.services.reviews import change_review, create_review, remove_review

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/",
    response_model=ReviewsResp,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_reviews(
    request: Request, session: asyncpg.Connection = Depends(get_session)
) -> ReviewsResp:
    rows = await get_reviews_from_db(session)

    reviews = [dict(row) for row in rows]

    return ReviewsResp(reviews=reviews)


@router.post(
    "/",
    response_model=CreateReviewResp,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_review(
    request: Request,
    feedback: UserFeedback,
    user_id: str = Security(verify_permissions, scopes=["reviews:create"]),
    session: asyncpg.Connection = Depends(get_session),
) -> CreateReviewResp:
    try:
        review_id = await create_review(user_id, feedback, session)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None

    return CreateReviewResp(id=review_id)


@router.put(
    "/{review_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ManageReviewResp,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def manage_review(
    request: Request,
    review_id: str,
    feedback: UserFeedback,
    user_id: str = Security(verify_permissions, scopes=["reviews:manage"]),
    session: asyncpg.Connection = Depends(get_session),
) -> ManageReviewResp:
    try:
        await change_review(review_id, feedback, session)
    except ReviewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        ) from None

    return ManageReviewResp()


@router.delete(
    "/{review_id}",
    response_model=DeleteReviewResp,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def delete_review(
    request: Request,
    review_id: str,
    user_id: str = Security(verify_permissions, scopes=["reviews:delete"]),
    session: asyncpg.Connection = Depends(get_session),
) -> DeleteReviewResp:
    try:
        await remove_review(review_id, session)
    except ReviewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        ) from None

    return DeleteReviewResp()
