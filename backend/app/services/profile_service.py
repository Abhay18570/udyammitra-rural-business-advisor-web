from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.business import BusinessProfile
from app.models.profile import EntrepreneurResource, EntrepreneurSkill, ExistingBusiness
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfileUpdate, SelectionItem


class ProfileService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.profiles = ProfileRepository(db)

    def get(self, user: User) -> ProfileResponse:
        profile = self.profiles.get_for_user(user)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrepreneur profile not found.")
        return self._response(user, profile)

    def upsert(self, user: User, payload: ProfileUpdate) -> ProfileResponse:
        if payload.proposed_business_id is not None:
            business = self.db.get(BusinessProfile, payload.proposed_business_id)
            if business is None or not business.is_active:
                raise HTTPException(status_code=422, detail="Select an active supported proposed business.")
        profile = self.profiles.get_for_user(user) or self.profiles.create_for_user(user)
        values = payload.model_dump(exclude_unset=True, exclude={"full_name", "preferred_language", "skills", "resources", "existing_business"})
        for field, value in values.items():
            setattr(profile, field, value)
        if payload.full_name is not None:
            user.full_name = " ".join(payload.full_name.strip().split())
        if payload.preferred_language is not None:
            user.preferred_language = payload.preferred_language
        if payload.skills is not None:
            for skill in list(profile.skills):
                self.db.delete(skill)
            self.db.flush()
            profile.skills = self._skills(payload.skills)
        if payload.resources is not None:
            for resource in list(profile.resources):
                self.db.delete(resource)
            self.db.flush()
            profile.resources = self._resources(payload.resources)
        if payload.has_existing_business is False:
            profile.existing_business = None
        elif payload.existing_business is not None:
            data = payload.existing_business.model_dump()
            if profile.existing_business:
                for field, value in data.items():
                    setattr(profile.existing_business, field, value)
            else:
                profile.existing_business = ExistingBusiness(**data)
        self.profiles.save(profile)
        return self._response(user, profile)

    @staticmethod
    def _skills(items: Iterable[SelectionItem]):
        return [EntrepreneurSkill(name=item.name, other_description=item.other_description) for item in items]

    @staticmethod
    def _resources(items: Iterable[SelectionItem]):
        return [EntrepreneurResource(name=item.name, other_description=item.other_description) for item in items]

    def _response(self, user: User, profile) -> ProfileResponse:
        business = self.db.get(BusinessProfile, profile.proposed_business_id) if profile.proposed_business_id else None
        return ProfileResponse(proposed_business_id=profile.proposed_business_id, proposed_business_name=business.name if business else None, full_name=user.full_name, preferred_language=user.preferred_language, age_group=profile.age_group, education=profile.education, previous_experience=profile.previous_experience, state=profile.state, district=profile.district, taluka=profile.taluka, village=profile.village, pincode=profile.pincode, latitude=profile.latitude, longitude=profile.longitude, capital_range=profile.capital_range, own_capital=profile.own_capital, loan_required=profile.loan_required, skills=[SelectionItem.model_validate(item, from_attributes=True) for item in profile.skills], resources=[SelectionItem.model_validate(item, from_attributes=True) for item in profile.resources], has_existing_business=profile.has_existing_business, existing_business=profile.existing_business, onboarding_step=profile.onboarding_step, onboarding_completed=profile.onboarding_completed)
