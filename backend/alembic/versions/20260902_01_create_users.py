"""create users table

Revision ID: 20260902_01
Revises:
Create Date: 2026-09-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260902_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("mobile_number", sa.String(length=10), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("preferred_language", sa.Enum("en", "mr", "hi", name="preferred_language", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("role", sa.Enum("USER", "ADMIN", "SUPER_ADMIN", name="user_role", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_mobile_number"), "users", ["mobile_number"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_mobile_number"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
