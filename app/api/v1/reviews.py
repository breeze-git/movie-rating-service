from fastapi import APIRouter, Depends, Request, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.repositories as repo
from app.database.session import get_session
from app.schemas.reviews import (
    ReviewCreateRequest,
    ReviewCreateResponse,
    ReviewDeleteResponse,
    ReviewManageResponse,
    ReviewsGetResponse,
)
from app.services.reviews import ReviewService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_permissions

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/",
    response_model=ReviewsGetResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_reviews(
    request: Request, session: AsyncSession = Depends(get_session)
) -> ReviewsGetResponse:
    reviews = await repo.get_reviews(session)

    return ReviewsGetResponse(reviews=reviews)  # type: ignore


@router.post(
    "/",
    response_model=ReviewCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_review(
    request: Request,
    review_data: ReviewCreateRequest,
    user_id: str = Security(verify_permissions, scopes=["reviews:create"]),
    review_service: ReviewService = Depends(),
) -> ReviewCreateResponse:

    id = await review_service.create_review(user_id, review_data)

    return ReviewCreateResponse(id=id)


@router.put(
    "/{review_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewManageResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def manage_review(
    request: Request,
    review_id: str,
    review_data: ReviewCreateRequest,
    user_id: str = Security(verify_permissions, scopes=["reviews:manage"]),
    review_service: ReviewService = Depends(),
) -> ReviewManageResponse:
    await review_service.manage_review(review_id, review_data)

    return ReviewManageResponse()


@router.delete(
    "/{review_id}",
    response_model=ReviewDeleteResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def delete_review(
    request: Request,
    review_id: str,
    user_id: str = Security(verify_permissions, scopes=["reviews:delete"]),
    review_service: ReviewService = Depends(),
) -> ReviewDeleteResponse:

    await review_service.remove_review(review_id)

    return ReviewDeleteResponse()
