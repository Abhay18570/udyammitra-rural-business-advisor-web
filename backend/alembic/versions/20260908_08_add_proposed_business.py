"""Persist optional proposed catalog business on entrepreneur profiles."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "20260908_08"
down_revision = "20260907_07"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("entrepreneur_profiles", sa.Column("proposed_business_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_profile_proposed_business", "entrepreneur_profiles", "business_profiles", ["proposed_business_id"], ["id"])
    op.create_index("ix_entrepreneur_profiles_proposed_business_id", "entrepreneur_profiles", ["proposed_business_id"])


def downgrade():
    op.drop_index("ix_entrepreneur_profiles_proposed_business_id", table_name="entrepreneur_profiles")
    op.drop_constraint("fk_profile_proposed_business", "entrepreneur_profiles", type_="foreignkey")
    op.drop_column("entrepreneur_profiles", "proposed_business_id")
