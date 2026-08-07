from uuid import uuid4

from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.http import NotEnoughRightsError
from app.database.models import Movie
from app.services.movies.exceptions import MovieNotFoundError
from tests.helpers import assert_error_response, assert_validation_error
from tests.schemas import MovieDTO
from tests.urls import urls


async def test_delete_movie_success(
    db_session: AsyncSession,
    admin_client: AsyncClient,
    created_movie_dto: MovieDTO,
):
    response = await admin_client.delete(urls.delete_movie(created_movie_dto.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db_session.expire_all()

    query = select(Movie).where(Movie.id == created_movie_dto.id)

    result = await db_session.scalar(query)

    assert result is None


async def test_delete_movie_not_found_fail(
    admin_client: AsyncClient,
):
    invalid_movie_id = str(uuid4())

    response = await admin_client.delete(urls.delete_movie(invalid_movie_id))

    assert_error_response(response, status.HTTP_404_NOT_FOUND, MovieNotFoundError.code)

    error_data = response.json()

    assert error_data["search_by"] == "id"
    assert error_data["search_value"] == invalid_movie_id


async def test_delete_not_enough_rights_fail(
    user_client: AsyncClient,
    created_movie_dto: MovieDTO,
):
    response = await user_client.delete(urls.delete_movie(created_movie_dto.id))

    assert_error_response(response, status.HTTP_403_FORBIDDEN, NotEnoughRightsError.code)


async def test_delete_movie_invalid_movie_id_fail(
    admin_client: AsyncClient,
):
    response = await admin_client.delete(urls.delete_movie("invalid_movie_id"))

    assert_validation_error(response, "movie_id")
