from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.v1 import v1_router
from app.database.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    yield

    await close_db()


app = FastAPI(title="movie-review-platform-api", lifespan=lifespan)

app.include_router(v1_router)


@app.get("/favicon.ico")
def get_favicon() -> FileResponse:
    return FileResponse("favicon.ico")
