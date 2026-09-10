"""Validated ingestion data, deliberately separate from future API contracts."""
from typing import Optional
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.models.government_scheme import SchemeLevel


class GovernmentSchemeImport(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scheme_name: str = Field(min_length=1, max_length=300)
    slug: str = Field(min_length=1, max_length=120, pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    details: str = Field(min_length=1)
    benefits: str = Field(min_length=1)
    eligibility: str = Field(min_length=1)
    application_process: Optional[str] = None
    documents_required: Optional[str] = None
    level: SchemeLevel
    state: Optional[str] = Field(default=None, max_length=100)
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source_type: Literal['DATASET'] = 'DATASET'
    source_dataset: str = Field(min_length=1, max_length=255)


# Public read contracts do not expose UUIDs or the generated search vector.
from datetime import datetime
from enum import Enum
from app.models.government_scheme import VerificationStatus

DISCOVERY_DISCLAIMER = 'Imported scheme information is discovery data and should be verified against current official sources before application.'


class GovernmentSchemeSort(str, Enum):
    NAME_ASC = 'name_asc'
    NAME_DESC = 'name_desc'
    NEWEST = 'newest'
    OLDEST = 'oldest'


class GovernmentSchemeQuery(BaseModel):
    page: int = Field(default=1, ge=1, le=2147483647)
    page_size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = Field(default=None, max_length=200, description='English PostgreSQL full-text search; blank means no search. Relevance sorts first.')
    level: Optional[SchemeLevel] = None
    state: Optional[str] = Field(default=None, min_length=1, max_length=100, description='Exact normalized state name or importer alias; excludes Central schemes.')
    category: Optional[str] = Field(default=None, min_length=1, max_length=200, description='Exact category label from /filters, including capitalization and internal commas.')
    verification_status: Optional[VerificationStatus] = None
    sort: GovernmentSchemeSort = GovernmentSchemeSort.NAME_ASC


class GovernmentSchemeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    scheme_name: str
    short_description: str
    level: SchemeLevel
    state: Optional[str]
    categories: list[str]
    tags: list[str]
    verification_status: VerificationStatus
    source_type: str


class GovernmentSchemePage(BaseModel):
    items: list[GovernmentSchemeListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    disclaimer: str = DISCOVERY_DISCLAIMER


class GovernmentSchemeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    scheme_name: str
    details: str
    benefits: str
    eligibility: str
    application_process: Optional[str]
    documents_required: Optional[str]
    level: SchemeLevel
    state: Optional[str]
    categories: list[str]
    tags: list[str]
    verification_status: VerificationStatus
    source_type: str
    source_dataset: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    disclaimer: str = DISCOVERY_DISCLAIMER


class GovernmentSchemeFilters(BaseModel):
    levels: list[SchemeLevel]
    states: list[str]
    categories: list[str]
    verification_statuses: list[VerificationStatus]
