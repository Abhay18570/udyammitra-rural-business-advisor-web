"""Typed evidence and immutable analysis contracts; provider payloads never enter requests."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, JsonValue, computed_field
from app.schemas.nearby_market import NearbyMarketResponse
from app.schemas.financial import FinancialAnalysisResponse
from app.schemas.scheme import SchemeAnalysisResponse


class BusinessAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    financial_analysis_id: uuid.UUID
    radius_km: int = Field(strict=True, ge=1, le=10)


class RequirementMatch(BaseModel):
    requirement: str
    status: Literal['CONFIRMED_SELF_REPORTED', 'TENTATIVE_ALIAS_MATCH', 'NOT_RECORDED']
    declared_value: Optional[str] = None


class EntrepreneurContext(BaseModel):
    enterprise_stage: Literal['NEW', 'EXISTING', 'UNKNOWN']
    declared_skills: List[str]
    declared_resources: List[str]
    skills: List[RequirementMatch]
    resources: List[RequirementMatch]
    existing_business_observations: Optional[Dict[str, Any]] = None


class BusinessContext(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    category: str
    business_type: str
    catalog_hash: str
    catalog_snapshot: Dict[str, Any]


class BudgetContext(BaseModel):
    own_capital: Optional[Decimal]
    financial_margin: Decimal
    consistency_status: Literal['CONSISTENT', 'DIFFERENT', 'NOT_RECORDED']


class Evidence(BaseModel):
    id: str
    value: JsonValue
    unit: Optional[str] = None
    source_kind: Literal['SELF_REPORTED', 'CATALOG_ASSUMPTION', 'CALCULATED', 'OBSERVED_LOCAL', 'DATA_LIMITATION', 'BUSINESS_BASELINE']
    source_ref: str
    observed_at: Optional[datetime] = None
    geography: Optional[str] = None
    radius_km: Optional[int] = None
    is_assumption: bool = False
    is_self_report: bool = False
    limitations: List[str] = Field(default_factory=list)

    @computed_field
    @property
    def value_type(self) -> str:
        if self.value is None:
            return 'null'
        return {dict: 'object', list: 'array', str: 'string', bool: 'boolean', int: 'number', float: 'number'}[type(self.value)]


class PricingItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    variable_unit_cost: Decimal = Field(ge=0, allow_inf_nan=False)
    monthly_volume: Decimal = Field(allow_inf_nan=False)
    allocated_monthly_fixed_cost: Decimal = Field(ge=0, allow_inf_nan=False)
    overhead_weight: Decimal = Field(ge=0, le=1, allow_inf_nan=False)
    target_margin_range: List[Decimal] = Field(min_length=2, max_length=2)
    source: str = Field(min_length=1)
    version: str = Field(min_length=1)


class PricingAssumptions(BaseModel):
    status: str = 'INSUFFICIENT_PRICING_ASSUMPTIONS'
    items: List[PricingItem] = Field(default_factory=list)
    monthly_fixed_cost: Optional[Decimal] = Field(default=None, ge=0, allow_inf_nan=False)
    version: str = 'pricing-v1'
    provenance: str = 'No structured catalog unit-cost or volume assumptions configured.'


class BusinessAnalysisContext(BaseModel):
    entrepreneur: EntrepreneurContext
    business: BusinessContext
    financial: FinancialAnalysisResponse
    scheme: SchemeAnalysisResponse
    budget: BudgetContext
    profile_fingerprint: str
    market: NearbyMarketResponse
    pricing_assumptions: PricingAssumptions = Field(default_factory=PricingAssumptions)
    evidence: List[Evidence]
    quality: Dict[str, List[str]]
    rule_versions: Dict[str, str]


class Threat(BaseModel):
    id: str
    rule_id: str
    threat_type: str
    evidence_kind: Literal['OBSERVED_LOCAL', 'SELF_REPORTED', 'INHERENT_BUSINESS_MODEL', 'DATA_LIMITATION']
    title: str
    description: str
    severity: Optional[Literal['LOW', 'MEDIUM', 'HIGH']] = None
    severity_reason: Optional[str] = None
    likelihood: Optional[Literal['LOW', 'MEDIUM', 'HIGH']] = None
    evidence_ids: List[str]
    mitigation: str
    source_refs: List[str]
    coverage_warnings: List[str] = Field(default_factory=list)


class SwotItem(BaseModel):
    source_type: Literal['BUSINESS_BASELINE', 'PROFILE', 'MARKET', 'FINANCIAL', 'CATALOG', 'DYNAMIC'] = 'DYNAMIC'
    id: str
    rule_id: str
    category: str
    title: str
    explanation: str
    importance: Optional[str] = None
    evidence_ids: List[str]
    finding_ids: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class BusinessAnalysisResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    business: BusinessContext
    profile_context: EntrepreneurContext
    financial_context: Dict[str, Any]
    market_context: NearbyMarketResponse
    swot: Dict[str, List[SwotItem]]
    local_threats: List[Threat]
    competition: Dict[str, Any]
    pricing: Dict[str, Any]
    evidence: List[Evidence]
    quality: Dict[str, Any]
