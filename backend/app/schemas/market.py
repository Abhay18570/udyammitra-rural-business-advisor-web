import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.business import BusinessCategory
from app.models.market import AmenityType, InstitutionType


class MarketLocation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    slug: str
    name: str
    village: str
    taluka: str
    district: str
    state: str
    pincode: Optional[str]
    latitude: float
    longitude: float
    is_demo: bool


class MarketLocationsResponse(BaseModel):
    locations: List[MarketLocation]
    resolved_location_slug: Optional[str]
    resolution_status: str
    data_version: str
    disclaimer: str


class MarketAnalysisRequest(BaseModel):
    radius_km: int
    demo_location_slug: Optional[str] = None


class DistributionChannel(BaseModel):
    type: AmenityType
    name: str
    distance_km: float


class LocalizedThreat(BaseModel):
    code: str
    explanation: str


class NearbyCompetitor(BaseModel):
    name: str
    category: BusinessCategory
    distance_km: float


class BusinessMarketResult(BaseModel):
    business_id: uuid.UUID
    business_slug: str
    business_name: str
    business_category: BusinessCategory
    competitors_0_2_km: int
    competitors_2_5_km: int
    competitors_5_10_km: int
    competitors_within_2_km: int
    competitors_within_5_km: int
    competitors_within_10_km: int
    competitors_within_selected_radius: int
    nearest_competitor_km: Optional[float]
    competition_intensity: int
    competition_label: str
    competition_opportunity_score: int
    demand_score: int
    demand_label: str
    market_reach_score: int
    market_access_score: int
    supply_chain_score: int
    distribution_channels: List[DistributionChannel]
    localized_threats: List[LocalizedThreat]
    evidence: List[str]
    nearby_competitors: List[NearbyCompetitor]
    market_opportunity_signal: int


class MarketMapPoint(BaseModel):
    kind: str
    name: str
    subtype: str
    latitude: float
    longitude: float
    distance_km: float


class MarketSummary(BaseModel):
    location: str
    radius_km: int
    business_points_considered: int
    institutions_considered: int
    amenities_considered: int
    lower_competition_categories: List[str]
    higher_demand_categories: List[str]
    strong_market_access_categories: List[str]


class MarketAnalysisResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    analysis_version: str
    data_version: str
    is_demo: bool
    disclaimer: str
    location_source: str
    selected_location: MarketLocation
    radius_km: int
    summary: MarketSummary
    businesses: List[BusinessMarketResult]
    map_points: List[MarketMapPoint]


class InstitutionEvidence(BaseModel):
    type: InstitutionType
    count: int
