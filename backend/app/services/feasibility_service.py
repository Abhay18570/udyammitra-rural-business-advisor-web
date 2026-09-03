import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.engines.feasibility_engine import evaluate_business, rank_results
from app.feasibility_rules import BUSINESS_FEASIBILITY_VERSION, DISCLAIMER
from app.models.feasibility import BusinessFeasibilityAnalysis
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.feasibility_repository import FeasibilityRepository
from app.repositories.market_repository import MarketRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.feasibility import FeasibilityRequest, FeasibilityResponse


class FeasibilityService:
    def __init__(self, db: Session) -> None:
        self.profiles = ProfileRepository(db)
        self.markets = MarketRepository(db)
        self.businesses = BusinessRepository(db)
        self.analyses = FeasibilityRepository(db)

    def analyze(self, user: User, payload: FeasibilityRequest) -> FeasibilityResponse:
        profile = self.profiles.get_for_user(user)
        if not profile or not profile.onboarding_completed:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "profile_required", "message": "Complete your entrepreneur profile before generating feasibility analysis."})
        if payload.market_analysis_id:
            market = self.markets.get_owned(payload.market_analysis_id, user.id)
            if not market:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market analysis not found.")
        else:
            market = self.markets.latest(user.id)
        if not market:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "market_analysis_required", "message": "Run and save local market analysis before generating feasibility analysis."})
        market_results = {item["business_id"]: item for item in market.result_snapshot.get("businesses", [])}
        results = []
        for business in self.businesses.list_active():
            evidence = market_results.get(str(business.id))
            if evidence:
                results.append(evaluate_business(profile, business, evidence))
        if not results:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "analysis_snapshot_unavailable", "message": "The selected market snapshot has no active supported business evidence."})
        ranked = rank_results(results)
        profile_snapshot = {
            "capital_range": profile.capital_range.value if profile.capital_range else None,
            "own_capital": str(profile.own_capital) if profile.own_capital is not None else None,
            "loan_required": str(profile.loan_required) if profile.loan_required is not None else None,
            "skills": [{"name": item.name, "other_description": item.other_description} for item in profile.skills],
            "resources": [{"name": item.name, "other_description": item.other_description} for item in profile.resources],
            "has_existing_business": profile.has_existing_business,
            "existing_business": ({"business_name": profile.existing_business.business_name, "business_category": profile.existing_business.business_category} if profile.existing_business else None),
            "location": {"state": profile.state, "district": profile.district, "taluka": profile.taluka, "village": profile.village, "pincode": profile.pincode},
        }
        snapshot = {"disclaimer": DISCLAIMER, "results": ranked, "top_matches": ranked[:3]}
        analysis = self.analyses.save(BusinessFeasibilityAnalysis(user_id=user.id, market_analysis_id=market.id, profile_snapshot=profile_snapshot, analysis_version=BUSINESS_FEASIBILITY_VERSION, market_analysis_version=market.analysis_version, market_data_version=market.data_version, results_snapshot=snapshot, created_at=datetime.now(timezone.utc)))
        return self._response(analysis)

    def latest(self, user: User) -> FeasibilityResponse:
        analysis = self.analyses.latest(user.id)
        if not analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No saved feasibility analysis found.")
        return self._response(analysis)

    def get(self, user: User, analysis_id: uuid.UUID) -> FeasibilityResponse:
        analysis = self.analyses.get_owned(analysis_id, user.id)
        if not analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feasibility analysis not found.")
        return self._response(analysis)

    @staticmethod
    def _response(analysis: BusinessFeasibilityAnalysis) -> FeasibilityResponse:
        return FeasibilityResponse.model_validate({"id": analysis.id, "created_at": analysis.created_at, "analysis_version": analysis.analysis_version, "market_analysis_id": analysis.market_analysis_id, "market_analysis_version": analysis.market_analysis_version, "market_data_version": analysis.market_data_version, **analysis.results_snapshot})
