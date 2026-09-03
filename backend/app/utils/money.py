"""Exact INR parsing, rounding, and presentation helpers."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Union

MoneyInput = Union[str, int, Decimal]
PAISE = Decimal("0.01")
WHOLE_RUPEE = Decimal("1")


def parse_inr(value: MoneyInput) -> Decimal:
    """Return a paise-precision Decimal; floats are rejected to prevent binary drift."""
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError("INR amounts must use a decimal string, integer, or Decimal.")
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Enter a valid INR amount.") from exc
    if not amount.is_finite():
        raise ValueError("Enter a finite INR amount.")
    return amount.quantize(PAISE, rounding=ROUND_HALF_UP)


def round_inr_to_rupee(value: MoneyInput) -> Decimal:
    return parse_inr(value).quantize(WHOLE_RUPEE, rounding=ROUND_HALF_UP)


def format_inr(value: MoneyInput, include_paise: bool = False) -> str:
    amount = parse_inr(value)
    if not include_paise:
        amount = amount.quantize(WHOLE_RUPEE, rounding=ROUND_HALF_UP)
    sign = "-" if amount < 0 else ""
    absolute = abs(amount)
    whole, _, fraction = format(absolute, ".2f").partition(".")
    tail = whole[-3:]
    head = whole[:-3]
    groups = []
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    grouped = ",".join([*groups, tail]) if groups else tail
    suffix = ".{}".format(fraction) if include_paise else ""
    return "{}₹{}{}".format(sign, grouped, suffix)
