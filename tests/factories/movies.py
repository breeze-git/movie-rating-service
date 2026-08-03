from uuid import uuid4

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from app.schemas.movies import MoviePayload


class MoviePayloadFactory(ModelFactory[MoviePayload]):
    __model__ = MoviePayload

    title = Use(ModelFactory.__faker__.name)
    description = Use(ModelFactory.__faker__.text)

    release_year: int = 2000
    director_id = Use(uuid4)

    country_ids: list = [1, 2, 3]
    genre_ids: list = [4, 5, 6]
