"""Shared vocabulary for deterministic analysis modules."""

import enum
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.business import BusinessCategory
from app.scheme_rules import SchemeType  # Re-export shared scheme vocabulary.


class AnalysisRadiusKm(int, enum.Enum):
    FIVE = 5
    TEN = 10


class EnterpriseStage(str, enum.Enum):
    NEW = "NEW"
    EXISTING = "EXISTING"


class CurrencyCode(str, enum.Enum):
    INR = "INR"


class MoneyRounding(str, enum.Enum):
    HALF_UP_TO_PAISE = "HALF_UP_TO_PAISE"


class SchemeStatus(str, enum.Enum):
    ELIGIBLE = "ELIGIBLE"
    ELIGIBLE_WITH_GAP = "ELIGIBLE_WITH_GAP"
    OUT_OF_SUPPORTED_RANGE = "OUT_OF_SUPPORTED_RANGE"
    INELIGIBLE = "INELIGIBLE"
    VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"


class CalculationStatus(str, enum.Enum):
    NOT_CALCULATED = "NOT_CALCULATED"
    CALCULATED = "CALCULATED"
    UNAVAILABLE = "UNAVAILABLE"


class AnalysisLocation(BaseModel):
    state: str = Field(min_length=2, max_length=100)
    district: str = Field(min_length=2, max_length=100)
    block: str = Field(min_length=2, max_length=100)
    village: str = Field(min_length=2, max_length=120)
    pincode: str = Field(pattern=r"^[1-9]\d{5}$")
    latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180)


class AnalysisInput(BaseModel):
    location: AnalysisLocation
    available_margin_capital: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    proposed_business_id: uuid.UUID
    proposed_business_category: BusinessCategory
    radius_km: AnalysisRadiusKm
    enterprise_stage: EnterpriseStage
    currency: CurrencyCode = CurrencyCode.INR


class FinancialResultContract(BaseModel):
    calculation_status: CalculationStatus
    scheme_status: SchemeStatus
    currency: CurrencyCode = CurrencyCode.INR
    rounding: MoneyRounding = MoneyRounding.HALF_UP_TO_PAISE
    feasible_project_cost: Optional[Decimal] = None
    maximum_loan_amount: Optional[Decimal] = None
    beneficiary_contribution: Optional[Decimal] = None
    funding_gap: Optional[Decimal] = None
