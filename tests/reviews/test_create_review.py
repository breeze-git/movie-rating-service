from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Movie, Review
from app.schemas.reviews import ReviewDetail
from app.services.movies.exceptions import MovieNotFoundError
from app.services.reviews.exceptions import ReviewAlreadyExistsError
from tests.factories.reviews import ReviewPayloadFactory
from tests.helpers import assert_error_response, assert_validation_error
from tests.urls import urls


async def test_create_review_success(
    db_session: AsyncSession,
    user_client: AsyncClient,
    created_movie: Movie,
):
    payload = ReviewPayloadFactory.build()

    response = await user_client.post(urls.create_review(created_movie.id), json=payload.model_dump(mode="json"))

    assert response.status_code == status.HTTP_201_CREATED

    raw_json = response.json()["data"]

    assert "id" in raw_json
    assert "created_at" in raw_json

    response_data = ReviewDetail.model_validate(raw_json)

    assert response_data.movie_id == created_movie.id
    assert response_data.message == payload.message

    db_session.expire_all()

    db_review = await db_session.get(Review, response_data.id)

    assert db_review is not None
    assert db_review.message == payload.message
    assert db_review.created_at == response_data.created_at
    assert db_review.updated_at is None
    assert db_review.rating == payload.rating

    await db_session.refresh(created_movie)
    assert created_movie.rating == db_review.rating


async def test_create_review_not_found_movie_fail(
    user_client: AsyncClient,
):
    payload = ReviewPayloadFactory.build()

    invalid_movie_id = uuid4()

    response = await user_client.post(
        urls.create_review(invalid_movie_id),
        json=payload.model_dump(mode="json"),
    )

    assert_error_response(response, status.HTTP_404_NOT_FOUND, MovieNotFoundError.code)


async def test_create_review_already_exists_fail(
    user_client: AsyncClient,
    created_movie: Movie,
):
    payload = ReviewPayloadFactory.build()

    response = await user_client.post(urls.create_review(created_movie.id), json=payload.model_dump(mode="json"))

    assert response.status_code == status.HTTP_201_CREATED

    response = await user_client.post(urls.create_review(created_movie.id), json=payload.model_dump(mode="json"))

    assert_error_response(response, status.HTTP_409_CONFLICT, ReviewAlreadyExistsError.code)

    error_data = response.json()

    assert error_data["conflict_reason"] == "composite_key"


async def test_create_review_unauthorized_fail(
    api_client: AsyncClient,
):
    payload = ReviewPayloadFactory.build()

    response = await api_client.post(
        urls.create_review("some_movie_id"),
        json=payload.model_dump(mode="json"),
    )

    assert_error_response(response, status.HTTP_401_UNAUTHORIZED, "HTTP_ERROR")


@pytest.mark.parametrize(
    "invalid_field, invalid_value, expected_error_loc",
    [
        ("message", "", "message"),
        ("rating", -10, "rating"),
    ],
    ids=["message", "rating"],
)
async def test_create_review_invalid_payload_fails(
    user_client: AsyncClient,
    invalid_field: str,
    invalid_value: str | int,
    expected_error_loc: str,
):
    payload_dict = ReviewPayloadFactory.build().model_dump(mode="json")
    payload_dict[invalid_field] = invalid_value

    response = await user_client.post(urls.create_review("some_movie_id"), json=payload_dict)

    assert_validation_error(response, expected_error_loc)
