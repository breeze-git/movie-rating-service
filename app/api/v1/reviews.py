from uuid import UUID

from fastapi import APIRouter, Depends, Request, Security, status

from app.schemas.common import CollectionEnvelope, ResponseEnvelope
from app.schemas.pagination import PaginationParams
from app.schemas.reviews import (
    ReviewCreateRequest,
    ReviewCreateResponse,
    ReviewDeleteResponse,
    ReviewManageResponse,
    ReviewPatchRequest,
    ReviewSort,
)
from app.services.reviews import ReviewService

from .dependencies import (
    IPBasedLimiter,
    RoleBasedLimiter,
    verify_global_permissions,
    verify_review_permissions,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/{movie_id}",
    response_model=ResponseEnvelope[CollectionEnvelope],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_reviews(
    request: Request,
    movie_id: UUID,
    sort: ReviewSort = Depends(),
    pagination: PaginationParams = Depends(),
    review_serviece: ReviewService = Depends(),
) -> ResponseEnvelope:
    review_collection = await review_serviece.get_movie_reviews(
        movie_id,
        sort=sort,
        pagination=pagination,
    )

    review_collection.limit = pagination.limit
    review_collection.offset = pagination.offset

    return ResponseEnvelope(data=review_collection)


@router.post(
    "/{movie_id}",
    response_model=ReviewCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_review(
    request: Request,
    review_data: ReviewCreateRequest,
    movie_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["reviews:create"]),
    review_service: ReviewService = Depends(),
) -> ReviewCreateResponse:
    id = await review_service.create_review(movie_id, user_id, review_data)

    return ReviewCreateResponse(id=id)


@router.patch(
    "/{review_id}",
    response_model=ReviewManageResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_review(
    request: Request,
    review_id: UUID,
    review_data: ReviewPatchRequest,
    user_id: UUID = Security(verify_review_permissions, scopes=["reviews:manage"]),
    review_service: ReviewService = Depends(),
) -> ReviewManageResponse:
    await review_service.update_review(review_id, review_data)

    return ReviewManageResponse()


@router.delete(
    "/{review_id}",
    response_model=ReviewDeleteResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def delete_review(
    request: Request,
    review_id: UUID,
    user_id: UUID = Security(verify_review_permissions, scopes=["reviews:delete"]),
    review_service: ReviewService = Depends(),
) -> ReviewDeleteResponse:
    await review_service.remove_review(review_id)

    return ReviewDeleteResponse()
