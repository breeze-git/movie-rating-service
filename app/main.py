from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.v1 import v1_router
from app.core.exceptions import register_exception_handlers
from app.core.logger import setup_logger
from app.core.settings import settings

setup_logger()

app = FastAPI(
    title="movie-review-platform-api",
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
