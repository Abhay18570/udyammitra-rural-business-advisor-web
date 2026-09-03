import pytest
from pydantic import ValidationError

from app.schemas.profile import ProfileUpdate

CANONICAL_CAPITAL_RANGES = [
    "UP_TO_50000",
    "RANGE_50000_TO_100000",
    "RANGE_100000_TO_250000",
    "RANGE_250000_TO_500000",
    "RANGE_500000_TO_1000000",
    "ABOVE_1000000",
]


@pytest.mark.parametrize("capital_range", CANONICAL_CAPITAL_RANGES)
def test_profile_schema_accepts_every_canonical_capital_range(capital_range: str) -> None:
    parsed = ProfileUpdate.model_validate({"capital_range": capital_range, "onboarding_step": 3})
    assert parsed.capital_range.value == capital_range


def test_profile_schema_rejects_legacy_capital_range() -> None:
    with pytest.raises(ValidationError):
        ProfileUpdate.model_validate({"capital_range": "100000_TO_300000", "onboarding_step": 3})
