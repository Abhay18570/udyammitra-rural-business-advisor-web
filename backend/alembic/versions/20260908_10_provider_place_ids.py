"""Allow provider-neutral string place IDs without changing existing OSM identity."""
from alembic import op
import sqlalchemy as sa

revision = '20260908_10'
down_revision = '20260908_09'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('market_pois', 'external_id', existing_type=sa.BigInteger(), type_=sa.String(255),
                    existing_nullable=False, postgresql_using='external_id::text')


def downgrade():
    # Refuse rather than delete nonnumeric provider identities during rollback.
    op.alter_column('market_pois', 'external_id', existing_type=sa.String(255), type_=sa.BigInteger(),
                    existing_nullable=False, postgresql_using='external_id::bigint')
