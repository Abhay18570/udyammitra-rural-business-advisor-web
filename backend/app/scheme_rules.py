"""Canonical SIH prototype financing metadata, not lender sanction criteria."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Tuple


class SchemeType(str, Enum):
    MICRO_FINANCE = "MICRO_FINANCE"
    TERM_LOAN = "TERM_LOAN"


SCHEME_RULES_VERSION = "scheme-v1"
MICRO_PROJECT_COST_MAX = Decimal("140000.00")
SUPPORTED_PROJECT_COST_MAX = Decimal("5000000.00")
SCHEME_DISCLAIMER = "This result applies SIH prototype financing rules only. Lender eligibility and terms require verification; this is not loan approval or sanction."


@dataclass(frozen=True)
class SchemeDefinition:
    type: SchemeType
    display_name: str
    project_cost_min: Decimal
    project_cost_max: Decimal
    maximum_loan_amount: Decimal
    annual_interest_rate_percent: Decimal
    tenure_months: int
    moratorium_months: int
    project_cost_min_inclusive: bool = False
    project_cost_max_inclusive: bool = True


SCHEMES: Tuple[SchemeDefinition, ...] = (
    SchemeDefinition(SchemeType.MICRO_FINANCE, "Micro Finance", Decimal("0.00"), MICRO_PROJECT_COST_MAX,
                     Decimal("125000.00"), Decimal("6.50"), 36, 3),
    SchemeDefinition(SchemeType.TERM_LOAN, "Term Loan", MICRO_PROJECT_COST_MAX, SUPPORTED_PROJECT_COST_MAX,
                     Decimal("4500000.00"), Decimal("8.00"), 84, 6),
)
