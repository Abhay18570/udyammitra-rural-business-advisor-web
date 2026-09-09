"""Immutable deterministic business-analysis snapshots."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = '20260908_09'
down_revision = '20260908_08'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('business_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('business_profiles.id'), nullable=False),
        sa.Column('financial_analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('financial_analyses.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('selected_radius', sa.Integer(), nullable=False),
        *[sa.Column(name, sa.String(64), nullable=False) for name in ['profile_fingerprint', 'location_fingerprint', 'catalog_hash', 'context_hash']],
        *[sa.Column(name, postgresql.JSONB(), nullable=False) for name in ['rule_versions', 'evidence_snapshot', 'result_snapshot']],
        sa.CheckConstraint('selected_radius BETWEEN 1 AND 10', name='ck_business_analysis_radius'))
    op.create_index('ix_business_analyses_user_id', 'business_analyses', ['user_id'])
    op.execute("""CREATE FUNCTION reject_business_analysis_update() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN RAISE EXCEPTION 'Business analysis snapshots are immutable'; END; $$""")
    op.execute('CREATE TRIGGER immutable_business_analysis BEFORE UPDATE ON business_analyses FOR EACH ROW EXECUTE FUNCTION reject_business_analysis_update()')


def downgrade():
    op.drop_table('business_analyses')
    op.execute('DROP FUNCTION reject_business_analysis_update()')
