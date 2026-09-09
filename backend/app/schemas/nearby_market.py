import uuid
from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class NearbyMarketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    radius_km: int = Field(strict=True, ge=1, le=10)
    business_query: Optional[str] = Field(default=None, min_length=2, max_length=200)
    business_slug: Optional[str] = Field(default=None, min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


    @field_validator('business_query', mode='before')
    @classmethod
    def clean_query(cls, value):
        return ' '.join(value.split()) if isinstance(value, str) else value

    @model_validator(mode='after')
    def require_intent(self):
        if not self.business_query and not self.business_slug:
            raise ValueError('Business query or catalog business is required')
        return self


class EvidenceWarning(BaseModel):
    code: str
    message: str


class ResolvedLocation(BaseModel):
    latitude: float
    longitude: float
    display_name: str
    query_used: str
    provider: str
    precision: str
    address: Dict[str, str]
    location_fingerprint: str
    fetched_at: datetime
    expires_at: datetime


class NearbyBusiness(BaseModel):
    id: Optional[uuid.UUID] = None
    slug: Optional[str] = None
    display_name: str


class NearbyPOI(BaseModel):
    provider: str
    external_type: Literal["node", "way", "relation", "place"]
    external_id: str
    name: str
    latitude: float
    longitude: float
    coordinate_kind: Literal["NODE", "REPRESENTATIVE_CENTER", "PLACE_LOCATION"]
    classification: Literal["DIRECT_COMPETITOR", "RELATED_BUSINESS", "GENERIC_POI"]
    matched_business_slug: str
    matching_rule: str
    matching_evidence: List[Dict[str, str]]
    normalized_tags: Dict[str, str]
    normalized_address: Dict[str, str]
    fetched_at: datetime
    distance_meters: float
    distance_km: str


class NearbySummary(BaseModel):
    direct_competitors: int
    related_businesses: int
    nearest_direct_competitor: Optional[NearbyPOI]


class NearbyRadius(BaseModel):
    selected_km: int
    selected_meters: int
    distance_method: Literal["POSTGIS_GEOGRAPHY_SPHEROID"] = "POSTGIS_GEOGRAPHY_SPHEROID"


class NearbySource(BaseModel):
    provider: Literal["OPENSTREETMAP_OVERPASS", "GOOGLE_PLACES"] = "OPENSTREETMAP_OVERPASS"
    mode: Literal["LIVE", "CACHE"]
    cache_status: Literal["FRESH_FETCH", "FRESH_CACHE", "STALE_CACHE"]
    fetched_at: datetime
    expires_at: datetime
    mapping_version: str


class NearbyQuality(BaseModel):
    complete_query: bool
    rejected_record_count: int
    warnings: List[EvidenceWarning]
    attribution: str = "© OpenStreetMap contributors (ODbL)"


class NearbyMarketResponse(BaseModel):
    business_query: Optional[str] = None
    matched_catalog_business_slug: Optional[str] = None
    business: NearbyBusiness
    location: ResolvedLocation
    radius: NearbyRadius
    summary: NearbySummary
    competitors: List[NearbyPOI]
    related_businesses: List[NearbyPOI]
    generic_pois: List[NearbyPOI] = Field(default_factory=list)
    source: NearbySource
    quality: NearbyQuality
