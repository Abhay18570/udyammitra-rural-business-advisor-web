import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.financial_rules import MAXIMUM_MARGIN_INPUT


class FinancialAnalysisRequest(BaseModel):
    business_slug: str = Field(min_length=1, max_length=100)
    available_margin_capital: Decimal
    feasibility_analysis_id: Optional[uuid.UUID] = None

    @field_validator("available_margin_capital", mode="before")
    @classmethod
    def exact_margin(cls, value):
        if isinstance(value, (float, bool)):
            raise ValueError("Available margin capital must be sent as a decimal string or integer, not a float.")
        try:
            amount = Decimal(value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("Enter a valid available margin capital amount.") from exc
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Available margin capital must be greater than zero.")
        if amount.as_tuple().exponent < -2:
            raise ValueError("Available margin capital supports at most two decimal places.")
        if amount > MAXIMUM_MARGIN_INPUT:
            raise ValueError("Available margin capital exceeds the ₹1 crore prototype input limit.")
        return amount.quantize(Decimal("0.01"))


class FinancialBusiness(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    category: str
    short_description: str


class FinancialWarning(BaseModel):
    code: str
    message: str


class BusinessCostAlignment(BaseModel):
    setup_cost_coverage_status: str
    financial_readiness_status: str
    funding_gap: str
    capacity_above_estimated_max: str
    comparison_explanation: str
    working_capital_explanation: str


class FinancialAnalysisResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    analysis_version: str
    feasibility_analysis_id: Optional[uuid.UUID]
    business: FinancialBusiness
    available_margin_capital: str
    beneficiary_contribution: str
    beneficiary_contribution_percentage: str = "10.00"
    feasible_project_cost: str
    indicative_loan_amount: str
    indicative_loan_percentage: str = "90.00"
    business_costs: dict
    alignment: BusinessCostAlignment
    warnings: List[FinancialWarning]
    disclaimer: str
    data_source_notice: str
    next_step: str
