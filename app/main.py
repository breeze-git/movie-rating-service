from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.v1 import v1_router
from app.core.exceptions import register_exception_handlers
from app.core.logger import setup_logger
from app.core.settings import settings
from app.database.session import close_db
from app.redis import redis_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_helper.init(settings.redis_url)

    yield

    await redis_helper.close()
    await close_db()


setup_logger()

app = FastAPI(
    title="movie-rating-service-api",
    lifespan=lifespan,
    docs_url="/docs" if settings.show_docs else None,
    redoc_url="/redoc" if settings.show_docs else None,
    openapi_url="/openapi.json" if settings.show_docs else None,
    debug=settings.debug,
)


app.include_router(v1_router)

register_exception_handlers(app)


@app.get("/favicon.ico")
def get_favicon() -> FileResponse:
    return FileResponse("favicon.ico")
