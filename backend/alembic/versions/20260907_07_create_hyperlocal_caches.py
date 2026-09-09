"""Add real geographic evidence caches without changing demo analyses.

Revision ID: 20260907_07
Revises: 20260904_06
"""
import geoalchemy2
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision = "20260907_07"
down_revision = "20260904_06"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("geocoding_cache",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("location_fingerprint", sa.String(64), nullable=False),
        sa.Column("status", sa.String(40), nullable=False), sa.Column("result", postgresql.JSONB(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_geocoding_cache_expires_at", "geocoding_cache", ["expires_at"])
    op.create_table("market_pois",
        sa.Column("id", sa.UUID(), primary_key=True), sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("external_type", sa.String(12), nullable=False), sa.Column("external_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(2000), nullable=False),
        sa.Column("geo_point", geoalchemy2.Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False),
        sa.Column("coordinate_kind", sa.String(30), nullable=False),
        sa.Column("normalized_tags", postgresql.JSONB(), nullable=False), sa.Column("normalized_address", postgresql.JSONB(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("provider", "external_type", "external_id", name="uq_market_poi_external"))
    op.create_index("ix_market_pois_geo_point", "market_pois", ["geo_point"], postgresql_using="gist")
    op.create_table("nearby_query_cache",
        sa.Column("key", sa.String(64), primary_key=True), sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False), sa.Column("radius_meters", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False), sa.Column("business_slug", sa.String(100), nullable=False),
        sa.Column("mapping_version", sa.String(40), nullable=False), sa.Column("poi_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        sa.Column("complete", sa.Boolean(), nullable=False), sa.Column("rejected_record_count", sa.Integer(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_nearby_query_cache_expires_at", "nearby_query_cache", ["expires_at"])
    op.create_table("provider_request_state",
        sa.Column("key", sa.String(100), primary_key=True), sa.Column("next_allowed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=False), sa.Column("lease_owner", sa.UUID(), nullable=True))


def downgrade():
    op.drop_table("provider_request_state")
    op.drop_table("nearby_query_cache")
    op.drop_table("market_pois")
    op.drop_table("geocoding_cache")
