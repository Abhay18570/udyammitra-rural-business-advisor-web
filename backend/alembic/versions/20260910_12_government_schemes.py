"""Create the independent government scheme discovery catalog."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = '20260910_12'
down_revision = '20260910_11'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'government_schemes',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('slug', sa.String(120), nullable=False),
        sa.Column('scheme_name', sa.String(300), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('benefits', sa.Text(), nullable=False),
        sa.Column('eligibility', sa.Text(), nullable=False),
        sa.Column('application_process', sa.Text(), nullable=True),
        sa.Column('documents_required', sa.Text(), nullable=True),
        sa.Column('level', sa.Enum('CENTRAL', 'STATE', native_enum=False, create_constraint=True, name='government_scheme_level'), nullable=False),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('categories', pg.JSONB(), nullable=False, server_default='[]'),
        sa.Column('tags', pg.JSONB(), nullable=False, server_default='[]'),
        sa.Column('source_type', sa.String(20), nullable=False, server_default='DATASET'),
        sa.Column('source_dataset', sa.String(255), nullable=False),
        sa.Column('verification_status', sa.Enum('DATASET_ONLY', 'OFFICIAL_SOURCE_LINKED', 'VERIFIED', 'STALE', native_enum=False, create_constraint=True, name='government_scheme_verification'), nullable=False, server_default='DATASET_ONLY'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('search_vector', pg.TSVECTOR(), sa.Computed("to_tsvector('english'::regconfig, scheme_name || ' ' || details || ' ' || eligibility || ' ' || benefits)", persisted=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("source_type = 'DATASET'", name='government_scheme_source_type'),
        sa.CheckConstraint("level = 'STATE' OR state IS NULL", name='government_scheme_central_state'),
        sa.CheckConstraint("jsonb_typeof(categories) = 'array' AND jsonb_typeof(tags) = 'array'", name='government_scheme_lists'),
    )
    for column in ('slug', 'scheme_name', 'level', 'state', 'verification_status', 'is_active'):
        op.create_index(f'ix_government_schemes_{column}', 'government_schemes', [column], unique=column == 'slug')
    for column in ('categories', 'tags', 'search_vector'):
        op.create_index(f'ix_government_schemes_{column}', 'government_schemes', [column], postgresql_using='gin')


def downgrade():
    op.drop_table('government_schemes')
