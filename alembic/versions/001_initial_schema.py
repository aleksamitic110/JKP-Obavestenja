"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # locations
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("name_ascii", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("level", sa.Text(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_locations_city", "locations", ["city"])
    op.create_index("idx_locations_parent", "locations", ["parent_id"])
    op.create_unique_constraint("idx_locations_name_city", "locations", ["name", "city"])

    # subscribers
    op.create_table(
        "subscribers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("token", sa.String(36), unique=True, nullable=False),
    )
    op.create_index("idx_subscribers_email", "subscribers", ["email"])
    op.create_index("idx_subscribers_token", "subscribers", ["token"])

    # subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subscriber_id", sa.Integer(), sa.ForeignKey("subscribers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("custom_keywords", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("utility_types", sa.ARRAY(sa.Text()), server_default=sa.text("ARRAY['water','power']")),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_subscriptions_subscriber", "subscriptions", ["subscriber_id"])
    op.create_index("idx_subscriptions_location", "subscriptions", ["location_id"])

    # scraper_sources
    op.create_table(
        "scraper_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("scraper_key", sa.String(100), unique=True, nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("utility_type", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("interval_minutes", sa.Integer(), server_default="120"),
        sa.Column("max_items", sa.Integer(), server_default="20"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("last_run_status", sa.Text(), server_default="'idle'"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # scraped_items
    op.create_table(
        "scraped_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("scraper_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("published_at", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.UniqueConstraint("source_id", "external_url"),
    )
    op.create_index("idx_scraped_items_source", "scraped_items", ["source_id"])
    op.create_index("idx_scraped_items_scraped_at", "scraped_items", [sa.text("scraped_at DESC")])

    # notification_log
    op.create_table(
        "notification_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subscriber_id", sa.Integer(), sa.ForeignKey("subscribers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("scraped_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("status", sa.Text(), server_default="'sent'"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.UniqueConstraint("subscriber_id", "item_id", "channel"),
    )
    op.create_index("idx_notification_log_subscriber", "notification_log", ["subscriber_id"])
    op.create_index("idx_notification_log_item", "notification_log", ["item_id"])


def downgrade() -> None:
    op.drop_table("notification_log")
    op.drop_table("scraped_items")
    op.drop_table("scraper_sources")
    op.drop_table("subscriptions")
    op.drop_table("subscribers")
    op.drop_table("locations")
