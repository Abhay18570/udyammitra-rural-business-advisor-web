"""create business feasibility analyses

Revision ID: 20260903_05
Revises: 20260903_04
Create Date: 2026-09-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260903_05"
down_revision: Union[str, None] = "20260903_04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_feasibility_analyses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("market_analysis_id", sa.UUID(), nullable=False),
        sa.Column("profile_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("analysis_version", sa.String(30), nullable=False),
        sa.Column("market_analysis_version", sa.String(30), nullable=False),
        sa.Column("market_data_version", sa.String(40), nullable=False),
        sa.Column("results_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["market_analysis_id"], ["market_analyses.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_business_feasibility_analyses_user_id", "business_feasibility_analyses", ["user_id"])
    op.create_index("ix_business_feasibility_analyses_market_analysis_id", "business_feasibility_analyses", ["market_analysis_id"])
    op.create_index("ix_business_feasibility_analyses_created_at", "business_feasibility_analyses", ["created_at"])
    op.create_index("ix_feasibility_user_created", "business_feasibility_analyses", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_table("business_feasibility_analyses")
