from uuid import UUID

from fastapi import APIRouter, Depends, Request, Security, status

from app.schemas.common import CollectionEnvelope, PaginationParams, ResponseEnvelope
from app.schemas.reviews import (
    ReviewDetail,
    ReviewPayload,
    ReviewSortCriteria,
    ReviewUpdate,
)
from app.services.reviews.service import ReviewService

from .dependencies import (
    IPBasedLimiter,
    RoleBasedLimiter,
    verify_global_permissions,
    verify_review_permissions,
)
from .openapi import errors_model

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/{movie_id}",
    response_model=ResponseEnvelope[CollectionEnvelope[ReviewDetail]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 404, 422, 429),
)
async def get_reviews(
    request: Request,
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

    review_collection.limit = pagination.limit
    review_collection.offset = pagination.offset

    return ResponseEnvelope(data=review_collection)


@router.post(
    "/{movie_id}",
    response_model=ResponseEnvelope[ReviewDetail],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 409, 422, 429),
)
async def post_review(
    request: Request,
    payload: ReviewPayload,
    movie_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["reviews:create"]),
    service: ReviewService = Depends(),
) -> ResponseEnvelope:
    review = await service.create_review(movie_id, user_id, payload)

    return ResponseEnvelope(data=review)


@router.patch(
    "/{review_id}",
    response_model=ResponseEnvelope[ReviewDetail],
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 409, 422, 429),
)
async def patch_review(
    request: Request,
    review_id: UUID,
    payload: ReviewUpdate,
    user_id: UUID = Security(verify_review_permissions, scopes=["reviews:update"]),
    service: ReviewService = Depends(),
) -> ResponseEnvelope:
    review = await service.update_review(review_id, payload)

    return ResponseEnvelope(data=review)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 422, 429),
)
async def delete_review(
    request: Request,
    review_id: UUID,
    user_id: UUID = Security(verify_review_permissions, scopes=["reviews:delete"]),
    review_service: ReviewService = Depends(),
) -> None:
    await review_service.remove_review(review_id)
