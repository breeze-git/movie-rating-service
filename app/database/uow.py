from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.repositories.director import DirectorRepository
from app.database.repositories.movie import MovieRepository
from app.database.repositories.review import ReviewRepository
from app.database.repositories.user import UserRepository
from app.database.session import get_session_maker


class UnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] = Depends(get_session_maker),
    ):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()

        self.users = UserRepository(self.session)
        self.reviews = ReviewRepository(self.session)
        self.movies = MovieRepository(self.session)
        self.directors = DirectorRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
