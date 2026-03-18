"""Add preferred_language to user_preferences

Revision ID: 002
Revises: 001
Create Date: 2026-03-17
"""
import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_preferences", sa.Column("preferred_language", sa.String(10), nullable=True))


def downgrade() -> None:
    op.drop_column("user_preferences", "preferred_language")
