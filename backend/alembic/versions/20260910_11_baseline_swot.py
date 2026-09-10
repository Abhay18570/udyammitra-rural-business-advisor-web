"""Add structured baseline business guidance without changing existing knowledge."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260910_11'
down_revision = '20260908_10'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('business_profiles', sa.Column('baseline_swot', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))


def downgrade():
    op.drop_column('business_profiles', 'baseline_swot')
