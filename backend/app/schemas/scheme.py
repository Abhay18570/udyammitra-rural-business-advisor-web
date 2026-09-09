import uuid
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict

from app.scheme_rules import SCHEME_DISCLAIMER, SCHEME_RULES_VERSION, SchemeType
from app.schemas.analysis import CalculationStatus, CurrencyCode, MoneyRounding, SchemeStatus
from app.schemas.financial import FinancialBusiness


class SchemeAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    financial_analysis_id: uuid.UUID


class SchemeExplanation(BaseModel):
    code: str
    params: Dict[str, str]
    message: str


class SchemeMetadata(BaseModel):
    type: SchemeType
    display_name: str
    project_cost_min: str
    project_cost_max: str
    project_cost_min_inclusive: bool
    project_cost_max_inclusive: bool
    maximum_loan_amount: str
    annual_interest_rate_percent: str
    tenure_months: int
    moratorium_months: int


class SchemeAnalysisResponse(BaseModel):
    financial_analysis_id: uuid.UUID
    financial_analysis_version: str
    scheme_rules_version: str = SCHEME_RULES_VERSION
    calculation_status: CalculationStatus = CalculationStatus.CALCULATED
    scheme_status: SchemeStatus
    currency: CurrencyCode = CurrencyCode.INR
    rounding: MoneyRounding = MoneyRounding.HALF_UP_TO_PAISE
    eligibility_basis: Literal["PROTOTYPE_FINANCING_RULES"] = "PROTOTYPE_FINANCING_RULES"
    verification_required: Literal[True] = True
    business: FinancialBusiness
    project_cost: str
    beneficiary_contribution: str
    financing_requirement: str
    indicative_financed_principal: Optional[str]
    scheme_financing_gap: Optional[str]
    fully_covered: Optional[bool]
    additional_contribution_required: Optional[str]
    total_contribution_required: Optional[str]
    scheme: Optional[SchemeMetadata]
    repayment_basis: None = None
    eligibility_reasons: List[SchemeExplanation]
    warnings: List[SchemeExplanation]
    next_steps: List[SchemeExplanation]
    disclaimer: str = SCHEME_DISCLAIMER


class GuidanceAnalysis(SchemeAnalysisResponse):
    financial_analysis_id: Optional[uuid.UUID] = None
    financial_analysis_version: Optional[str] = None
    business: Optional[FinancialBusiness] = None


class SchemeGuidanceResponse(BaseModel):
    source: Literal['SAVED_FINANCIAL_PLAN', 'PROFILE_ILLUSTRATION', 'FINANCIAL_PLAN_REQUIRED']
    result: Optional[GuidanceAnalysis] = None
    rules: List[SchemeMetadata]
    scheme_rules_version: str = SCHEME_RULES_VERSION
    funding_share_percent: str
    contribution_share_percent: str
    setup_funding_gap: Optional[str] = None
    source_observed_at: Optional[str] = None
    notice: Optional[Literal['CONTRIBUTION_UNUSABLE']] = None
    disclaimer: str = SCHEME_DISCLAIMER
