from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric, String, Text


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    director_id: Mapped[UUID] = mapped_column(ForeignKey("directors.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    release_year: Mapped[int] = mapped_column(index=True)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 1), index=True)

    reviews: Mapped[list["Review"]] = relationship(back_populates="movie")
    director: Mapped["Director"] = relationship(back_populates="movies")
    countries: Mapped[list["Country"]] = relationship(
        secondary="country_movies", back_populates="movies", passive_deletes=True
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary="genre_movies", back_populates="movies", passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "release_year >= 1895 AND release_year <= EXTRACT(YEAR FROM NOW())",
            name="check_release_year",
        ),
        UniqueConstraint(
            "title",
            "release_year",
            "director_id",
            name="uq_movie_title_year_director",
        ),
        Index(
            "movie_search_trgm_idx",
            text("title gin_trgm_ops"),
            postgresql_using="gin",
        ),
    )


class Director(Base):
    __tablename__ = "directors"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    date_of_birth: Mapped[date]

    movies: Mapped[list["Movie"]] = relationship(back_populates="director")

    __table_args__ = (
        CheckConstraint(
            "EXTRACT(YEAR FROM AGE(date_of_birth)) > 7",
            name="check_min_director_age",
        ),
        UniqueConstraint(
            "first_name",
            "last_name",
            "date_of_birth",
            name="uq_director_full_name_date_of_birth",
        ),
        Index(
            "directors_search_trgm_idx",
            text("(first_name || ' ' || last_name) gin_trgm_ops"),
            postgresql_using="gin",
        ),
    )


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)

    movies: Mapped[list["Movie"]] = relationship(
        secondary="country_movies", back_populates="countries", passive_deletes=True
    )


class CountryMovies(Base):
    __tablename__ = "country_movies"

    movie_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), primary_key=True, index=True
    )


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)

    movies: Mapped[list["Movie"]] = relationship(
        secondary="genre_movies", back_populates="genres", passive_deletes=True
    )


class GenreMovies(Base):
    __tablename__ = "genre_movies"

    movie_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True, index=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    username: Mapped[str] = mapped_column(String(50), unique=True)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(60))

    reviews: Mapped[list["Review"]] = relationship(back_populates="user", passive_deletes=True)
    roles: Mapped[list["Role"]] = relationship(secondary="user_roles", back_populates="users", passive_deletes=True)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    movie_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, index=True)
    rating: Mapped[int | None] = mapped_column(default=None, index=True)

    user: Mapped[User] = relationship(back_populates="reviews")
    movie: Mapped["Movie"] = relationship(back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating IS NULL OR rating BETWEEN 1 AND 10", name="check_rating"),
        UniqueConstraint(
            "user_id",
            "movie_id",
            name="uq_review_user_id_movie_id",
        ),
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    users: Mapped[list["User"]] = relationship(secondary="user_roles", back_populates="roles", passive_deletes=True)
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions", back_populates="roles", passive_deletes=True
    )


class UserRoles(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, index=True)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary="role_permissions", back_populates="permissions", passive_deletes=True
    )


class RolePermissions(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, index=True
    )
