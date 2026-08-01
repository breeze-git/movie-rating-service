"""seed_lookup_data

Revision ID: c2cde09d07c0
Revises: 2fca807a5f7c
Create Date: 2026-07-29 18:06:58.916332

"""

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c2cde09d07c0"
down_revision: Union[str, Sequence[str], None] = "2fca807a5f7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PARENT_DIR = Path(__file__).resolve().parent.parent

JSON_PATH = PARENT_DIR / "countries.json"


def upgrade() -> None:
    """Upgrade schema."""

    # COUNTRIES

    with open(JSON_PATH, "r", encoding="UTF-8") as f:
        countries = json.load(f)

    for country in countries:
        query = sa.text("""
            INSERT INTO countries (name) 
            VALUES (:name)
            ON CONFLICT DO NOTHING;
        """)

        op.get_bind().execute(query, {"name": country["name"]})

    # GENRES

    op.execute("""
        INSERT INTO genres (name)
        VALUES ('Action'), ('Adventure'), ('Animation'), 
               ('Comedy'), ('Crime'), ('Documentary'), 
               ('Drama'), ('Family'), ('Fantasy'), 
               ('History'), ('Horror'), ('Music'), 
               ('Mystery'), ('Romance'), ('Science Fiction'), 
               ('TV Movie'), ('Thriller'), ('War'), ('Western')
        ON CONFLICT DO NOTHING;
    """)

    # ROLES

    op.execute("""
        INSERT INTO roles (name)
        VALUES ('admin'), ('user')
        ON CONFLICT DO NOTHING;
    """)

    # PERMISSIONS

    op.execute("""
        INSERT INTO permissions (name)
        VALUES ('movies:create'), ('movies:update'), ('movies:delete'),
               ('directors:create'), ('directors:update'), ('directors:delete'),
        	   ('reviews:create'), ('reviews:update'), ('reviews:delete')
        ON CONFLICT (id) DO NOTHING;
    """)

    # ROLE_PERMISSIONS

    op.execute("""
        INSERT INTO public.role_permissions (role_id, permission_id)
        VALUES 
          ((SELECT id FROM roles WHERE name = 'user'),  (SELECT id FROM permissions WHERE name = 'reviews:create')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'movies:create')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'movies:update')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'movies:delete')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'directors:create')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'directors:update')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'directors:delete')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'reviews:create')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'reviews:update')),
          ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'reviews:delete'))
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("TRUNCATE TABLE countries CASCADE;")
    op.execute("TRUNCATE TABLE genres CASCADE;")
    op.execute("TRUNCATE TABLE permissions CASCADE;")
    op.execute("TRUNCATE TABLE roles CASCADE;")
