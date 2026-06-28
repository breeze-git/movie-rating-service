from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.v1 import v1_router
from app.core.exceptions import register_exception_handler

app = FastAPI(title="movie-review-platform-api")


app.include_router(v1_router)

register_exception_handler(app)


@app.get("/favicon.ico")
def get_favicon() -> FileResponse:
    return FileResponse("favicon.ico")
