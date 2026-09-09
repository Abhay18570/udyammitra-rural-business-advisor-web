import uuid
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.profile import AgeGroup, CapitalRange, EducationLevel, ExperienceLevel
from app.models.user import PreferredLanguage

SKILL_VALUES = {"Tailoring", "Repairing", "Farming", "Dairy", "Cooking", "Retail", "Machinery", "Computer", "Food Processing", "Driving", "Other"}
RESOURCE_VALUES = {"Land", "Shop", "Vehicle", "Storage Space", "Machinery", "Livestock", "Electricity", "Water", "Internet", "Other"}


class SelectionItem(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    other_description: Optional[str] = Field(default=None, max_length=120)


class ExistingBusinessPayload(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    business_category: str = Field(min_length=2, max_length=120)
    years_operating: int = Field(ge=0, le=100)
    initial_investment: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    monthly_revenue: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    monthly_expenses: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    employee_count: int = Field(ge=0, le=100000)
    estimated_monthly_customers: int = Field(ge=0, le=100000000)
    major_challenges: Optional[str] = Field(default=None, max_length=2000)


class ProfileUpdate(BaseModel):
    proposed_business_id: Optional[uuid.UUID] = None
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    preferred_language: Optional[PreferredLanguage] = None
    age_group: Optional[AgeGroup] = None
    education: Optional[EducationLevel] = None
    previous_experience: Optional[ExperienceLevel] = None
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    district: Optional[str] = Field(default=None, min_length=2, max_length=100)
    taluka: Optional[str] = Field(default=None, min_length=2, max_length=100)
    village: Optional[str] = Field(default=None, min_length=2, max_length=120)
    pincode: Optional[str] = Field(default=None, pattern=r"^[1-9]\d{5}$")
    latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180)
    capital_range: Optional[CapitalRange] = None
    own_capital: Optional[Decimal] = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    loan_required: Optional[Decimal] = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    skills: Optional[List[SelectionItem]] = None
    resources: Optional[List[SelectionItem]] = None
    has_existing_business: Optional[bool] = None
    existing_business: Optional[ExistingBusinessPayload] = None
    onboarding_step: int = Field(ge=1, le=6)
    onboarding_completed: bool = False

    @model_validator(mode="after")
    def validate_conditional_data(self) -> "ProfileUpdate":
        if self.skills is not None:
            self._validate_selections(self.skills, SKILL_VALUES, "skill")
        if self.resources is not None:
            self._validate_selections(self.resources, RESOURCE_VALUES, "resource")
        if self.has_existing_business is False and self.existing_business is not None:
            raise ValueError("Existing business details must be omitted when no current business is selected.")
        if self.has_existing_business is True and self.onboarding_completed and self.existing_business is None:
            raise ValueError("Existing business details are required to complete onboarding.")
        if self.onboarding_completed:
            required = [self.age_group, self.state, self.district, self.taluka, self.village, self.pincode, self.capital_range, self.own_capital, self.loan_required, self.has_existing_business]
            if any(value is None for value in required):
                raise ValueError("Complete all required profile fields before finishing onboarding.")
        return self

    @staticmethod
    def _validate_selections(items: List[SelectionItem], allowed: set, label: str) -> None:
        names = [item.name for item in items]
        if len(names) != len(set(names)) or any(name not in allowed for name in names):
            raise ValueError("Invalid or duplicate {} selection.".format(label))
        for item in items:
            if item.name == "Other" and not item.other_description:
                raise ValueError("Describe the Other {} selection.".format(label))


class ExistingBusinessResponse(ExistingBusinessPayload):
    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    proposed_business_id: Optional[uuid.UUID] = None
    proposed_business_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
    full_name: str
    preferred_language: PreferredLanguage
    age_group: Optional[AgeGroup]
    education: Optional[EducationLevel]
    previous_experience: Optional[ExperienceLevel]
    state: Optional[str]
    district: Optional[str]
    taluka: Optional[str]
    village: Optional[str]
    pincode: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    capital_range: Optional[CapitalRange]
    own_capital: Optional[Decimal]
    loan_required: Optional[Decimal]
    skills: List[SelectionItem]
    resources: List[SelectionItem]
    has_existing_business: Optional[bool]
    existing_business: Optional[ExistingBusinessResponse]
    onboarding_step: int
    onboarding_completed: bool
