from datetime import date
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.http import NotEnoughRightsError
from app.database.models import Movie
from app.schemas.movies import MovieDetail, MoviePayload
from app.services.directors.exceptions import DirectorNotFoundError
from app.services.movies.exceptions import (
    CountriesNotFoundError,
    GenresNotFoundError,
    MovieAlreadyExistsError,
)
from tests.factories.movies import MoviePayloadFactory
from tests.helpers import assert_error_response, assert_validation_error
from tests.schemas import DirectorDTO
from tests.urls import urls


async def test_create_movie_success(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    created_director_dto: DirectorDTO,
) -> None:
    movie_payload = MoviePayloadFactory.build(director_id=created_director_dto.id)

    response = await admin_client.post(urls.create_movie, json=movie_payload.model_dump(mode="json"))

    assert response.status_code == status.HTTP_201_CREATED

    response_data = MovieDetail.model_validate(response.json()["data"])

    assert response_data.director.id == created_director_dto.id
    assert response_data.description == movie_payload.description

    query = select(Movie).where(Movie.id == response_data.id)

    db_movie = await db_session.scalar(query)

    assert db_movie is not None
    assert db_movie.title == movie_payload.title
    assert db_movie.description == movie_payload.description
    assert db_movie.rating == response_data.rating


async def test_create_movie_not_found_director_fail(
    admin_client: AsyncClient,
) -> None:
    movie_payload = MoviePayloadFactory.build()

    response = await admin_client.post(urls.create_movie, json=movie_payload.model_dump(mode="json"))

    assert_error_response(response, status.HTTP_404_NOT_FOUND, DirectorNotFoundError.code)

    error_data = response.json()

    assert error_data["search_by"] == "id"
    assert error_data["search_value"] == str(movie_payload.director_id)


async def test_create_movie_not_enough_rights_fail(
    user_client: AsyncClient,
) -> None:
    movie_payload = MoviePayloadFactory.build()

    response = await user_client.post(urls.create_movie, json=movie_payload.model_dump(mode="json"))

    assert_error_response(response, status.HTTP_403_FORBIDDEN, NotEnoughRightsError.code)


async def test_create_movie_duplicate_fail(
    admin_client: AsyncClient,
    created_movie_payload: MoviePayload,
) -> None:
    response = await admin_client.post(urls.create_movie, json=created_movie_payload.model_dump(mode="json"))

    assert_error_response(response, status.HTTP_409_CONFLICT, MovieAlreadyExistsError.code)

    error_data = response.json()

    assert error_data["conflict_reason"] == "composite_key"


@pytest.mark.parametrize(
    "invalid_field, invalid_value, expected_error_code",
    [
        ("genre_ids", [-1, -2, -3], GenresNotFoundError.code),
        ("country_ids", [-4, -5, -6], CountriesNotFoundError.code),
    ],
    ids=["genre_ids", "country_ids"],
)
async def test_create_movie_not_found_genre_ids_country_ids_fails(
    admin_client: AsyncClient,
    created_director_dto: DirectorDTO,
    invalid_field: str,
    invalid_value: Any,
    expected_error_code: str,
):
    payload_dict = MoviePayloadFactory.build(director_id=created_director_dto.id).model_dump(mode="json")

    payload_dict[invalid_field] = invalid_value

    response = await admin_client.post(urls.create_movie, json=payload_dict)

    assert_error_response(response, status.HTTP_404_NOT_FOUND, expected_error_code)

    error_data = response.json()

    assert error_data["search_by"] == "id"
    assert error_data["search_value"] == invalid_value


@pytest.mark.parametrize(
    "invalid_field, invalid_value, expected_error_loc",
    [
        ("director_id", "invalid_director_id", "director_id"),
        ("title", " ", "title"),
        ("description", " ", "description"),
        ("release_year", date.today().year + 1, "release_year"),
        ("country_ids", [], "country_ids"),
        ("genre_ids", [], "genre_ids"),
    ],
    ids=[
        "director_id",
        "title",
        "description",
        "release_year",
        "country_ids",
        "genre_ids",
    ],
)
async def test_create_movie_invalid_payload_fails(
    admin_client: AsyncClient,
    invalid_field: str,
    invalid_value: Any,
    expected_error_loc: str,
):
    payload_dict = MoviePayloadFactory.build().model_dump(mode="json")

    payload_dict[invalid_field] = invalid_value

    response = await admin_client.post(urls.create_movie, json=payload_dict)

    assert_validation_error(response, expected_error_loc)
