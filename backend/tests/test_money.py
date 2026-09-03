from decimal import Decimal

import pytest

from app.utils.money import format_inr, parse_inr, round_inr_to_rupee


@pytest.mark.parametrize(("raw", "expected"), [
    ("0", Decimal("0.00")),
    ("100000.5", Decimal("100000.50")),
    ("1.005", Decimal("1.01")),
    (7, Decimal("7.00")),
    (Decimal("999.999"), Decimal("1000.00")),
])
def test_parse_inr_uses_paise_precision_and_half_up_rounding(raw, expected: Decimal) -> None:
    assert parse_inr(raw) == expected


@pytest.mark.parametrize("raw", [1.1, True, "not-money", "NaN", "Infinity"])
def test_parse_inr_rejects_unsafe_or_invalid_values(raw) -> None:
    with pytest.raises(ValueError):
        parse_inr(raw)


def test_format_inr_uses_indian_grouping() -> None:
    assert format_inr("1234567.49") == "₹12,34,567"
    assert format_inr("1234567.50") == "₹12,34,568"
    assert format_inr("-1234567.50", include_paise=True) == "-₹12,34,567.50"


def test_round_inr_to_whole_rupee_is_half_up() -> None:
    assert round_inr_to_rupee("10.49") == Decimal("10")
    assert round_inr_to_rupee("10.50") == Decimal("11")
