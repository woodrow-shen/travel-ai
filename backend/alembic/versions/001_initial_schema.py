"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-01

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("google_id", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column(
            "tier",
            sa.Enum("basic", "premium", name="usertier"),
            nullable=False,
            server_default="basic",
        ),
        sa.Column("tier_updated_at", sa.DateTime(timezone=True)),
        sa.Column("last_login", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # User Preferences
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("preferred_airlines", postgresql.ARRAY(sa.String(10))),
        sa.Column("excluded_airlines", postgresql.ARRAY(sa.String(10))),
        sa.Column("preferred_alliances", postgresql.ARRAY(sa.String(50))),
        sa.Column("cabin_classes", postgresql.ARRAY(sa.String(20))),
        sa.Column("max_stops", sa.Integer),
        sa.Column("home_airports", postgresql.ARRAY(sa.String(10))),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Trips
    op.create_table(
        "trips",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("destination", sa.String(255)),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("metadata", postgresql.JSONB),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Flights
    op.create_table(
        "flights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "trip_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("trips.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("airline", sa.String(10), nullable=False),
        sa.Column("flight_no", sa.String(20), nullable=False),
        sa.Column("origin", sa.String(10), nullable=False, index=True),
        sa.Column("destination", sa.String(10), nullable=False, index=True),
        sa.Column("departure", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stops", sa.Integer, server_default="0"),
        sa.Column("duration_minutes", sa.Integer),
        sa.Column("cabin_class", sa.String(20)),
        sa.Column("price_amount", sa.Float),
        sa.Column("price_currency", sa.String(10)),
        sa.Column("source", sa.String(50)),
        sa.Column("raw_data", postgresql.JSONB),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Hotels
    op.create_table(
        "hotels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "trip_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("trips.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("location", sa.String(500)),
        sa.Column("check_in", sa.Date),
        sa.Column("check_out", sa.Date),
        sa.Column("stars", sa.Integer),
        sa.Column("rating", sa.Float),
        sa.Column("price_per_night", sa.Float),
        sa.Column("price_currency", sa.String(10)),
        sa.Column("source", sa.String(50)),
        sa.Column("description", sa.Text),
        sa.Column("raw_data", postgresql.JSONB),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Activities
    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "trip_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("trips.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("location", sa.String(500)),
        sa.Column("description", sa.Text),
        sa.Column("start_time", sa.DateTime(timezone=True)),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column("price_amount", sa.Float),
        sa.Column("price_currency", sa.String(10)),
        sa.Column("category", sa.String(100)),
        sa.Column("source", sa.String(50)),
        sa.Column("raw_data", postgresql.JSONB),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Price History
    op.create_table(
        "price_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("origin", sa.String(10), nullable=False, index=True),
        sa.Column("destination", sa.String(10), nullable=False, index=True),
        sa.Column("departure_date", sa.Date, nullable=False, index=True),
        sa.Column("return_date", sa.Date),
        sa.Column("airline", sa.String(10)),
        sa.Column("price_amount", sa.Float, nullable=False),
        sa.Column("price_currency", sa.String(10), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("cabin_class", sa.String(20)),
        sa.Column("stops", sa.Integer),
        sa.Column("raw_data", postgresql.JSONB),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Itineraries
    op.create_table(
        "itineraries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "trip_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("trips.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("schedule", postgresql.JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Chat Sessions
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255)),
        sa.Column("messages", postgresql.JSONB, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Subscription Emails
    op.create_table(
        "subscription_emails",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "email_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subscription_emails.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Enum("bug_fare", "price_drop", "deal_digest", name="subscriptiontype"),
            nullable=False,
        ),
        sa.Column("config", postgresql.JSONB, server_default="{}"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("last_sent_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Notification Log
    op.create_table(
        "notification_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "subscription_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subscriptions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("sent", "failed", name="notificationstatus"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("notification_log")
    op.drop_table("subscriptions")
    op.drop_table("subscription_emails")
    op.drop_table("chat_sessions")
    op.drop_table("itineraries")
    op.drop_table("price_history")
    op.drop_table("activities")
    op.drop_table("hotels")
    op.drop_table("flights")
    op.drop_table("trips")
    op.drop_table("user_preferences")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS usertier")
    op.execute("DROP TYPE IF EXISTS subscriptiontype")
    op.execute("DROP TYPE IF EXISTS notificationstatus")
