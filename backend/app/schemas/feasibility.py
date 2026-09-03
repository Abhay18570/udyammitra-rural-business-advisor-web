import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class FeasibilityRequest(BaseModel):
    market_analysis_id: Optional[uuid.UUID] = None


class ScoreComponent(BaseModel):
    code: str
    title: str
    score: int
    weight: Decimal
    weighted_contribution: Decimal


class ExplanationItem(BaseModel):
    code: str
    title: str
    explanation: str


class GapItem(BaseModel):
    code: str
    severity: str
    explanation: str


class SkillEvidence(BaseModel):
    matched_required_skills: List[str]
    missing_required_skills: List[str]
    matched_preferred_skills: List[str]
    skill_match_score: int


class ResourceEvidence(BaseModel):
    available_required_resources: List[str]
    missing_required_resources: List[str]
    available_optional_resources: List[str]
    resource_readiness_score: int


class FeasibilityResult(BaseModel):
    rank: int
    business_id: uuid.UUID
    business_slug: str
    business_name: str
    business_category: str
    short_description: str
    final_feasibility_score: int
    feasibility_label: str
    is_current_business: bool
    components: List[ScoreComponent]
    skills: SkillEvidence
    resources: ResourceEvidence
    capital_fit_explanation: str
    financing_may_be_required: bool
    strengths: List[ExplanationItem]
    gaps: List[GapItem]
    next_actions: List[str]
    market_threats: List[dict]


class FeasibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    analysis_version: str
    market_analysis_id: uuid.UUID
    market_analysis_version: str
    market_data_version: str
    disclaimer: str
    results: List[FeasibilityResult]
    top_matches: List[FeasibilityResult]
