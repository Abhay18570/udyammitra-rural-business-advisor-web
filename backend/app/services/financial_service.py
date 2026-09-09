import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.engines.financial_engine import calculate_financial_analysis
from app.financial_rules import BENEFICIARY_MARGIN_RATE, LOAN_SHARE_RATE, BUSINESS_DATA_NOTICE, FINANCIAL_ANALYSIS_VERSION, FINANCIAL_DISCLAIMER
from app.models.financial import FinancialAnalysis
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.feasibility_repository import FeasibilityRepository
from app.repositories.financial_repository import FinancialRepository
from app.schemas.financial import FinancialAnalysisRequest, FinancialAnalysisResponse
from app.utils.money import parse_inr


def money(value) -> str:
    return format(parse_inr(value), ".2f")


class FinancialService:
    def __init__(self, db: Session) -> None:
        self.businesses = BusinessRepository(db); self.feasibility = FeasibilityRepository(db); self.analyses = FinancialRepository(db)

    def analyze(self, user: User, payload: FinancialAnalysisRequest) -> FinancialAnalysisResponse:
        business = self.businesses.get_active(payload.business_slug)
        if not business: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active business profile not found.")
        if payload.feasibility_analysis_id and not self.feasibility.get_owned(payload.feasibility_analysis_id, user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feasibility analysis not found.")
        calculated = calculate_financial_analysis(payload.available_margin_capital, business)
        costs = {
            "minimum_capital": money(business.minimum_capital),
            "maximum_capital": money(business.maximum_capital),
            "setup_cost_min": money(business.estimated_setup_cost_min),
            "setup_cost_max": money(business.estimated_setup_cost_max),
            "estimated_setup_cost_min": money(business.estimated_setup_cost_min),
            "estimated_setup_cost_max": money(business.estimated_setup_cost_max),
            "working_capital_min": money(business.working_capital_min),
            "working_capital_max": money(business.working_capital_max),
        }
        result = {
            "business": {
                "id": str(business.id),
                "slug": business.slug,
                "name": business.name,
                "category": business.category.value,
                "short_description": business.short_description,
            },
            "alignment": {
                key: money(value) if key in {"funding_gap", "capacity_above_estimated_max"} else value
                for key, value in calculated.items()
                if key in {"setup_cost_coverage_status", "financial_readiness_status", "funding_gap", "capacity_above_estimated_max", "comparison_explanation", "working_capital_explanation"}
            },
            "warnings": calculated["warnings"],
            "disclaimer": FINANCIAL_DISCLAIMER,
            "data_source_notice": BUSINESS_DATA_NOTICE,
            "next_step": "Check the financing option and loan-cap coverage for this saved calculation.",
        }
        analysis = self.analyses.save(FinancialAnalysis(
            user_id=user.id,
            business_profile_id=business.id,
            feasibility_analysis_id=payload.feasibility_analysis_id,
            available_margin_capital=calculated["available_margin_capital"],
            beneficiary_contribution=calculated["beneficiary_contribution"],
            feasible_project_cost=calculated["feasible_project_cost"],
            indicative_loan_amount=calculated["indicative_loan_amount"],
            funding_gap=calculated["funding_gap"],
            analysis_version=FINANCIAL_ANALYSIS_VERSION,
            business_cost_snapshot=costs,
            result_snapshot=result,
            created_at=datetime.now(timezone.utc),
        ))
        return self._response(analysis)

    def latest(self, user: User, business_slug: Optional[str] = None) -> FinancialAnalysisResponse:
        business_id = None
        if business_slug:
            business = self.businesses.get_active(business_slug)
            if not business: raise HTTPException(status_code=404, detail="Active business profile not found.")
            business_id = business.id
        analysis = self.analyses.latest(user.id, business_id)
        if not analysis: raise HTTPException(status_code=404, detail="No saved financial analysis found.")
        return self._response(analysis)

    def get(self, user: User, analysis_id: uuid.UUID) -> FinancialAnalysisResponse:
        analysis = self.analyses.get_owned(analysis_id, user.id)
        if not analysis: raise HTTPException(status_code=404, detail="Financial analysis not found.")
        return self._response(analysis)

    @staticmethod
    def _response(analysis: FinancialAnalysis) -> FinancialAnalysisResponse:
        return FinancialAnalysisResponse.model_validate({
            "id": analysis.id,
            "created_at": analysis.created_at,
            "analysis_version": analysis.analysis_version,
            "feasibility_analysis_id": analysis.feasibility_analysis_id,
            "available_margin_capital": money(analysis.available_margin_capital),
            "beneficiary_contribution": money(analysis.beneficiary_contribution),
            "beneficiary_contribution_percentage": format(BENEFICIARY_MARGIN_RATE * 100, ".2f"),
            "feasible_project_cost": money(analysis.feasible_project_cost),
            "indicative_loan_amount": money(analysis.indicative_loan_amount),
            "indicative_loan_percentage": format(LOAN_SHARE_RATE * 100, ".2f"),
            "business_costs": analysis.business_cost_snapshot,
            **analysis.result_snapshot,
        })
