from dataclasses import dataclass
from uuid import UUID

from app.main import app


@dataclass(frozen=True)
class URLPaths:
    register_user: str = app.url_path_for("register_user")
    login_user: str = app.url_path_for("login_user")
    logout_user: str = app.url_path_for("logout_user")
    update_user: str = app.url_path_for("update_user")
    refresh_token: str = app.url_path_for("refresh_token")
    create_movie: str = app.url_path_for("create_movie")
    search_movies: str = app.url_path_for("search_movies")

    @staticmethod
    def get_movie(movie_id: int | str | UUID) -> str:
        return app.url_path_for("get_movie", movie_id=str(movie_id))

    @staticmethod
    def delete_movie(movie_id: int | str | UUID) -> str:
        return app.url_path_for("delete_movie", movie_id=str(movie_id))

    @staticmethod
    def create_review(movie_id: int | str | UUID) -> str:
        return app.url_path_for("create_review", movie_id=str(movie_id))


urls = URLPaths()
