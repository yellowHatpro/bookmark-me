"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("cookies_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("extra_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ok"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "account_id",
            sa.Integer(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=256), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("author_handle", sa.String(length=256), nullable=True),
        sa.Column("author_name", sa.String(length=256), nullable=True),
        sa.Column("media_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("platform", "external_id", name="uq_bookmark_platform_external"),
    )
    op.create_index("ix_bookmark_saved_at", "bookmarks", ["saved_at"])
    op.create_index("ix_bookmark_platform", "bookmarks", ["platform"])

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "account_id",
            sa.Integer(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ok", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("new_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sync_runs")
    op.drop_index("ix_bookmark_platform", table_name="bookmarks")
    op.drop_index("ix_bookmark_saved_at", table_name="bookmarks")
    op.drop_table("bookmarks")
    op.drop_table("accounts")
