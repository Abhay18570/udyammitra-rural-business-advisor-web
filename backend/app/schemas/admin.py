from pydantic import BaseModel, Field


class AdminOverview(BaseModel):
    total_registered_users: int = Field(ge=0)
    total_entrepreneurs: int = Field(ge=0)
    profiles_pending: int = Field(ge=0)
    new_enterprises: int = Field(ge=0)
    existing_enterprises: int = Field(ge=0)
    states_count: int = Field(ge=0)
    districts_count: int = Field(ge=0)


from datetime import datetime
from typing import Literal, Optional


class GeographicRow(BaseModel):
    entrepreneur_count: int
    percentage: str
    new_enterprises: int
    existing_enterprises: int


class StateRow(GeographicRow):
    state: str
    state_key: str
    districts_count: int


class StateAnalytics(BaseModel):
    total_entrepreneurs: int
    located_entrepreneurs: int
    missing_state_count: int
    states_count: int
    districts_count: int
    states: list[StateRow]


class DistrictRow(GeographicRow):
    district: str
    district_key: str


class DistrictAnalytics(BaseModel):
    state: str
    state_key: str
    total_entrepreneurs: int
    districts_count: int
    missing_district_count: int
    new_enterprises: int
    existing_enterprises: int
    districts: list[DistrictRow]


class EntrepreneurItem(BaseModel):
    full_name: str
    email: str
    mobile_number: str
    state: Optional[str]
    district: Optional[str]
    taluka: Optional[str]
    village: Optional[str]
    enterprise_status: Literal['new', 'existing', 'unspecified']
    proposed_business: Optional[str]
    preferred_language: str
    created_at: datetime
    profile_status: Literal['complete', 'created', 'pending']


class EntrepreneurPage(BaseModel):
    items: list[EntrepreneurItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class EntrepreneurFilters(BaseModel):
    page: int = Field(default=1, ge=1, le=1_000_000)
    page_size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = Field(default=None, max_length=160)
    state: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    enterprise_status: Optional[Literal['new', 'existing', 'unspecified']] = None
    sort: Literal['created_desc', 'created_asc'] = 'created_desc'
    business_slug: Optional[str] = Field(default=None, max_length=100)
