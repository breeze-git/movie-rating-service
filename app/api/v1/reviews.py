from uuid import UUID

from fastapi import APIRouter, Depends, Security, status

from app.schemas.common import CollectionEnvelope, PaginationParams, ResponseEnvelope
from app.schemas.reviews import (
    ReviewDetail,
    ReviewPayload,
    ReviewSortCriteria,
    ReviewUpdate,
)
from app.services.reviews.service import ReviewService

from .dependencies import verify_global_permissions, verify_review_permissions
from .limiters import IPBasedLimiter, RoleBasedLimiter
from .openapi import errors_model

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/{movie_id}",
    summary="List reviews",
    response_model=ResponseEnvelope[CollectionEnvelope[ReviewDetail]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 404, 422, 429),
)
async def get_movie_reviews(
    movie_id: UUID,
    sort: ReviewSortCriteria = Depends(),
    pagination: PaginationParams = Depends(),
    service: ReviewService = Depends(),
) -> ResponseEnvelope:
    review_collection = await service.get_movie_reviews(
        movie_id,
        sort=sort,
        pagination=pagination,
    )

    return ResponseEnvelope(data=review_collection)


@router.get(
    "/{user_id}",
    summary="List reviews",
    response_model=ResponseEnvelope[CollectionEnvelope[ReviewDetail]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 404, 422, 429),
)
async def get_user_reviews(
    user_id: UUID,
    sort: ReviewSortCriteria = Depends(),
    pagination: PaginationParams = Depends(),
    service: ReviewService = Depends(),
) -> ResponseEnvelope:
    review_collection = await service.get_movie_reviews(
        user_id,
        sort=sort,
        pagination=pagination,
    )

    return ResponseEnvelope(data=review_collection)


@router.post(
    "/{movie_id}",
    name="create_review",
    summary="Create a review",
    response_model=ResponseEnvelope[ReviewDetail],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 409, 422, 429),
)
async def post_review(
    payload: ReviewPayload,
    movie_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["reviews:create"]),
    service: ReviewService = Depends(),
) -> ResponseEnvelope:
    review = await service.create_review(movie_id, user_id, payload)

    return ResponseEnvelope(data=review)


@router.patch(
    "/{review_id}",
    summary="Update a review",
    response_model=ResponseEnvelope[ReviewDetail],
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 409, 422, 429),
)
async def patch_review(
    review_id: UUID,
    payload: ReviewUpdate,
    user_id: UUID = Security(verify_review_permissions, scopes=["reviews:update"]),
    service: ReviewService = Depends(),
) -> ResponseEnvelope:
    review = await service.update_review(review_id, payload)

    return ResponseEnvelope(data=review)


@router.delete(
    "/{review_id}",
    summary="Delete a review",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 422, 429),
)
async def delete_review(
    review_id: UUID,
    user_id: UUID = Security(verify_review_permissions, scopes=["reviews:delete"]),
    review_service: ReviewService = Depends(),
) -> None:
    await review_service.remove_review(review_id)
