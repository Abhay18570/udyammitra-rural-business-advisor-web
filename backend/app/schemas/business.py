import uuid
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.business import BusinessCategory, BusinessType


class BusinessListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    slug: str
    name: str
    category: BusinessCategory
    business_type: BusinessType
    short_description: str
    minimum_capital: Decimal
    maximum_capital: Decimal
    is_active: bool


class BusinessDetail(BusinessListItem):
    detailed_description: str
    estimated_setup_cost_min: Decimal
    estimated_setup_cost_max: Decimal
    working_capital_min: Decimal
    working_capital_max: Decimal
    required_skills: List[str] = Field(min_length=1)
    preferred_skills: List[str]
    required_resources: List[str] = Field(min_length=1)
    optional_resources: List[str]
    equipment: List[str] = Field(min_length=1)
    customer_segments: List[str] = Field(min_length=1)
    market_drivers: List[str] = Field(min_length=1)
    competition_factors: List[str] = Field(min_length=1)
    supply_chain_factors: List[str] = Field(min_length=1)
    major_risks: List[str] = Field(min_length=1)
    required_registrations: List[str] = Field(min_length=1)
    operating_requirements: List[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_ranges_and_knowledge(self) -> "BusinessDetail":
        ranges = [(self.minimum_capital, self.maximum_capital), (self.estimated_setup_cost_min, self.estimated_setup_cost_max), (self.working_capital_min, self.working_capital_max)]
        if any(low < 0 or high < low for low, high in ranges):
            raise ValueError("Business cost ranges must be non-negative and ordered.")
        knowledge = [self.required_skills, self.preferred_skills, self.required_resources, self.optional_resources, self.equipment, self.customer_segments, self.market_drivers, self.competition_factors, self.supply_chain_factors, self.major_risks, self.required_registrations, self.operating_requirements]
        if any(any(not item.strip() for item in items) for items in knowledge):
            raise ValueError("Business knowledge items must not be blank.")
        return self
