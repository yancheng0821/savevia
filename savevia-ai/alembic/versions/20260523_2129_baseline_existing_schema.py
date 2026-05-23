"""baseline existing schema

Revision ID: 733282911def
Revises:
Create Date: 2026-05-23 21:29:40.655962
"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision = "733282911def"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op: schema is established by docker/mysql/init/*.sql.
    Alembic is baselined here for future schema changes only."""
    pass


def downgrade() -> None:
    """No-op."""
    pass
