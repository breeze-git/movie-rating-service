from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from app.schemas.reviews import ReviewPayload


class ReviewPayloadFactory(ModelFactory[ReviewPayload]):
    __model__ = ReviewPayload

    message = Use(ModelFactory.__faker__.text)
