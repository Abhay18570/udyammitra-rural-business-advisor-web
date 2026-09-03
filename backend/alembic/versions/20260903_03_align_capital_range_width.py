"""align canonical capital range storage width

Revision ID: 20260903_03
Revises: 20260903_02
Create Date: 2026-09-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_03"
down_revision: Union[str, None] = "20260903_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "entrepreneur_profiles",
        "capital_range",
        existing_type=sa.String(length=30),
        type_=sa.String(length=23),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "entrepreneur_profiles",
        "capital_range",
        existing_type=sa.String(length=23),
        type_=sa.String(length=30),
        existing_nullable=True,
    )
