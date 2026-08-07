from collections.abc import Callable

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.factories.movies import MoviePayloadFactory
from tests.helpers import assert_validation_error
from tests.schemas import DirectorDTO
from tests.urls import urls


async def test_search_movies_success(
    api_client: AsyncClient,
    create_movie_in_db: Callable,
    created_director_dto: DirectorDTO,
):
    other_movie_payload = MoviePayloadFactory.build(title="Some title", director_id=created_director_dto.id)

    await create_movie_in_db(other_movie_payload)

    payload = MoviePayloadFactory.build(
        title="Pirates of the Caribbean: The Curse of the Black Pearl",
        director_id=created_director_dto.id,
    )

    matching_movie = await create_movie_in_db(payload)

    query_params = {
        "search": "pirates",
        "genre_ids": payload.genre_ids,
        "limit": 10,
        "offset": 0,
    }

    response = await api_client.get(urls.search_movies, params=query_params)

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()["data"]

    assert response_data["limit"] == 10
    assert response_data["offset"] == 0

    items = response_data["items"]

    assert len(items) == 1
    assert items[0]["id"] == str(matching_movie.id)
    assert items[0]["title"] == "Pirates of the Caribbean: The Curse of the Black Pearl"


@pytest.mark.parametrize(
    "invalid_params, expected_error_loc",
    [
        ({"search": "a" * 101}, "search"),
        ({"genre_ids": list(range(1, 22))}, "genre_ids"),
        ({"country_ids": list(range(1, 22))}, "country_ids"),
        ({"director_ids": ["invalid-uuid"]}, "director_ids"),
    ],
    ids=["search", "genre_ids", "country_ids", "director_ids"],
)
async def test_search_movies_invalid_payload_fails(
    api_client: AsyncClient,
    invalid_params: dict,
    expected_error_loc: str,
):
    response = await api_client.get(urls.search_movies, params=invalid_params)

    assert_validation_error(response, expected_error_loc)
