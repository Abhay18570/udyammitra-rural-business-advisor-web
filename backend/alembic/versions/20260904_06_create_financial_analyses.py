"""create financial analysis snapshots

Revision ID: 20260904_06
Revises: 20260903_05
Create Date: 2026-09-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260904_06"
down_revision: Union[str, None] = "20260903_05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "financial_analyses",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("user_id", sa.UUID(), nullable=False), sa.Column("business_profile_id", sa.UUID(), nullable=False), sa.Column("feasibility_analysis_id", sa.UUID()),
        sa.Column("available_margin_capital", sa.Numeric(14, 2), nullable=False), sa.Column("beneficiary_contribution", sa.Numeric(14, 2), nullable=False), sa.Column("feasible_project_cost", sa.Numeric(14, 2), nullable=False), sa.Column("indicative_loan_amount", sa.Numeric(14, 2), nullable=False), sa.Column("funding_gap", sa.Numeric(14, 2), nullable=False),
        sa.Column("analysis_version", sa.String(30), nullable=False), sa.Column("business_cost_snapshot", postgresql.JSONB(), nullable=False), sa.Column("result_snapshot", postgresql.JSONB(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_profile_id"], ["business_profiles.id"]), sa.ForeignKeyConstraint(["feasibility_analysis_id"], ["business_feasibility_analyses.id"]), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_financial_analyses_user_id", "financial_analyses", ["user_id"])
    op.create_index("ix_financial_analyses_business_profile_id", "financial_analyses", ["business_profile_id"])
    op.create_index("ix_financial_analyses_feasibility_analysis_id", "financial_analyses", ["feasibility_analysis_id"])
    op.create_index("ix_financial_analyses_created_at", "financial_analyses", ["created_at"])
    op.create_index("ix_financial_user_business_created", "financial_analyses", ["user_id", "business_profile_id", "created_at"])


def downgrade() -> None:
    op.drop_table("financial_analyses")
