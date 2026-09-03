"""canonicalize capital range values

Revision ID: 20260903_02
Revises: 1261ac4e3bd3
Create Date: 2026-09-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_02"
down_revision: Union[str, None] = "1261ac4e3bd3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CANONICAL = (
    "UP_TO_50000", "RANGE_50000_TO_100000", "RANGE_100000_TO_250000",
    "RANGE_250000_TO_500000", "RANGE_500000_TO_1000000", "ABOVE_1000000",
)
LEGACY = (
    "UP_TO_50000", "50000_TO_100000", "100000_TO_250000",
    "250000_TO_500000", "500000_TO_1000000", "ABOVE_1000000",
)


def _check(values: tuple[str, ...]) -> sa.CheckConstraint:
    allowed = ", ".join("'{}'".format(value) for value in values)
    return sa.CheckConstraint("capital_range IN ({})".format(allowed), name="capital_range")


def upgrade() -> None:
    op.drop_constraint("capital_range", "entrepreneur_profiles", type_="check")
    op.alter_column(
        "entrepreneur_profiles",
        "capital_range",
        existing_type=sa.String(length=17),
        type_=sa.String(length=30),
        existing_nullable=True,
    )
    for old, new in zip(LEGACY, CANONICAL):
        if old != new:
            op.execute(sa.text("UPDATE entrepreneur_profiles SET capital_range = :new WHERE capital_range = :old").bindparams(old=old, new=new))
    op.create_check_constraint(_check(CANONICAL).name, "entrepreneur_profiles", _check(CANONICAL).sqltext)


def downgrade() -> None:
    op.drop_constraint("capital_range", "entrepreneur_profiles", type_="check")
    for canonical, legacy in zip(CANONICAL, LEGACY):
        if canonical != legacy:
            op.execute(sa.text("UPDATE entrepreneur_profiles SET capital_range = :legacy WHERE capital_range = :canonical").bindparams(legacy=legacy, canonical=canonical))
    op.alter_column(
        "entrepreneur_profiles",
        "capital_range",
        existing_type=sa.String(length=30),
        type_=sa.String(length=17),
        existing_nullable=True,
    )
    op.create_check_constraint(_check(LEGACY).name, "entrepreneur_profiles", _check(LEGACY).sqltext)
