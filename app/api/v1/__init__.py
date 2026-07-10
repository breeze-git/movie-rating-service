from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.directors import router as directors_router
from app.api.v1.movies import router as movies_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.users import router as users_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(movies_router)
v1_router.include_router(directors_router)
v1_router.include_router(reviews_router)
v1_router.include_router(users_router)
