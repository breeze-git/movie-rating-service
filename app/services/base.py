from collections.abc import Callable, Mapping
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.repositories import RepositoryException
from app.core.exceptions.services import ServiceException, UnexpectedServiceError


class BaseService:
    _integrity_map: Mapping[str, Callable[[RepositoryException, Any], ServiceException]] = {}

    def __init__(self, session: AsyncSession):
        self.session = session

    def _handle_repo_error(self, exc: RepositoryException, **context: Any) -> ServiceException:
        error_factory = self._integrity_map.get(exc.constraint)

        if error_factory:
            return error_factory(exc, context)

        return UnexpectedServiceError(internal_msg=f"Unhandled database constraint violated: {exc.constraint}")
