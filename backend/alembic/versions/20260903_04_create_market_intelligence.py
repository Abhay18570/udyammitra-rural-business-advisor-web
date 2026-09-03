"""create hyper-local market intelligence tables

Revision ID: 20260903_04
Revises: 20260903_03
Create Date: 2026-09-03
"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260903_04"
down_revision: Union[str, None] = "20260903_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    geography = geoalchemy2.Geography(geometry_type="POINT", srid=4326, spatial_index=False)
    op.create_table(
        "demo_locations",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("slug", sa.String(100), nullable=False), sa.Column("name", sa.String(120), nullable=False),
        sa.Column("village", sa.String(120), nullable=False), sa.Column("taluka", sa.String(100), nullable=False), sa.Column("district", sa.String(100), nullable=False), sa.Column("state", sa.String(100), nullable=False), sa.Column("pincode", sa.String(6)),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False), sa.Column("longitude", sa.Numeric(9, 6), nullable=False), sa.Column("geo_point", geography, nullable=False),
        sa.Column("settlement_density_signal", sa.Integer(), nullable=False), sa.Column("agriculture_intensity_signal", sa.Integer(), nullable=False), sa.Column("commercial_activity_signal", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("is_demo", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_demo_locations_slug", "demo_locations", ["slug"], unique=True)
    op.create_index("ix_demo_locations_geo_point", "demo_locations", ["geo_point"], postgresql_using="gist")
    op.create_table(
        "demo_local_businesses",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("demo_location_id", sa.UUID(), nullable=False), sa.Column("business_profile_id", sa.UUID()), sa.Column("seed_key", sa.String(120), nullable=False), sa.Column("name", sa.String(160), nullable=False),
        sa.Column("category", sa.Enum("RETAIL", "SERVICES", "AGRICULTURE", "FOOD_PROCESSING", "MANUFACTURING", name="demo_market_business_category", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("business_type", sa.Enum("SERVICE", "RETAIL", "AGRI_ALLIED", "PROCESSING", "RENTAL", name="demo_market_business_type", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False), sa.Column("longitude", sa.Numeric(9, 6), nullable=False), sa.Column("geo_point", geography, nullable=False), sa.Column("source_label", sa.String(160), nullable=False), sa.Column("is_demo", sa.Boolean(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_profile_id"], ["business_profiles.id"], ondelete="SET NULL"), sa.ForeignKeyConstraint(["demo_location_id"], ["demo_locations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("demo_location_id", "seed_key", name="uq_demo_local_business_seed"),
    )
    op.create_index("ix_demo_local_businesses_demo_location_id", "demo_local_businesses", ["demo_location_id"])
    op.create_index("ix_demo_local_businesses_business_profile_id", "demo_local_businesses", ["business_profile_id"])
    op.create_index("ix_demo_local_businesses_geo_point", "demo_local_businesses", ["geo_point"], postgresql_using="gist")
    op.create_table(
        "demo_institutions",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("demo_location_id", sa.UUID(), nullable=False), sa.Column("name", sa.String(160), nullable=False),
        sa.Column("institution_type", sa.Enum("SCHOOL", "COLLEGE", "HOSPITAL", "PRIMARY_HEALTH_CENTRE", "BANK", "GRAM_PANCHAYAT", "MARKET", "BUS_STAND", "AGRICULTURAL_MARKET", "INDUSTRIAL_CLUSTER", name="institution_type", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False), sa.Column("longitude", sa.Numeric(9, 6), nullable=False), sa.Column("geo_point", geography, nullable=False), sa.Column("is_demo", sa.Boolean(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["demo_location_id"], ["demo_locations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("demo_location_id", "name", name="uq_demo_institution_name"),
    )
    op.create_index("ix_demo_institutions_demo_location_id", "demo_institutions", ["demo_location_id"])
    op.create_index("ix_demo_institutions_geo_point", "demo_institutions", ["geo_point"], postgresql_using="gist")
    op.create_table(
        "demo_amenities",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("demo_location_id", sa.UUID(), nullable=False), sa.Column("name", sa.String(160), nullable=False),
        sa.Column("amenity_type", sa.Enum("MARKET", "BUS_STAND", "MAJOR_ROAD", "BANK", "WAREHOUSE", "COLD_STORAGE", "TRANSPORT_NODE", "AGRI_MARKET", "COLLECTION_CENTRE", name="amenity_type", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False), sa.Column("longitude", sa.Numeric(9, 6), nullable=False), sa.Column("geo_point", geography, nullable=False), sa.Column("is_demo", sa.Boolean(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["demo_location_id"], ["demo_locations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("demo_location_id", "name", name="uq_demo_amenity_name"),
    )
    op.create_index("ix_demo_amenities_demo_location_id", "demo_amenities", ["demo_location_id"])
    op.create_index("ix_demo_amenities_geo_point", "demo_amenities", ["geo_point"], postgresql_using="gist")
    op.create_table(
        "market_analyses",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("user_id", sa.UUID(), nullable=False), sa.Column("demo_location_id", sa.UUID(), nullable=False), sa.Column("profile_location_snapshot", postgresql.JSONB(), nullable=False), sa.Column("analysis_radius_km", sa.Integer(), nullable=False), sa.Column("analysis_version", sa.String(30), nullable=False), sa.Column("data_version", sa.String(40), nullable=False), sa.Column("result_snapshot", postgresql.JSONB(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["demo_location_id"], ["demo_locations.id"]), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.CheckConstraint("analysis_radius_km IN (5, 10)", name="ck_market_analysis_radius"),
    )
    op.create_index("ix_market_analyses_user_id", "market_analyses", ["user_id"])
    op.create_index("ix_market_analyses_demo_location_id", "market_analyses", ["demo_location_id"])
    op.create_index("ix_market_analyses_created_at", "market_analyses", ["created_at"])


def downgrade() -> None:
    op.drop_table("market_analyses")
    op.drop_index("ix_demo_amenities_geo_point", table_name="demo_amenities")
    op.drop_table("demo_amenities")
    op.drop_index("ix_demo_institutions_geo_point", table_name="demo_institutions")
    op.drop_table("demo_institutions")
    op.drop_index("ix_demo_local_businesses_geo_point", table_name="demo_local_businesses")
    op.drop_table("demo_local_businesses")
    op.drop_index("ix_demo_locations_geo_point", table_name="demo_locations")
    op.drop_table("demo_locations")
