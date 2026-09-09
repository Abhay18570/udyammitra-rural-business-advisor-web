from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.engines.financial_engine import calculate_structure
from app.engines.scheme_engine import evaluate_scheme
from app.financial_rules import FINANCIAL_ANALYSIS_VERSION, MAXIMUM_MARGIN_INPUT
from app.models.user import User
from app.repositories.financial_repository import FinancialRepository
from app.schemas.financial import FinancialBusiness
from app.schemas.scheme import SchemeAnalysisRequest, SchemeAnalysisResponse
from app.utils.money import parse_inr


def serialize_decimals(value):
    if isinstance(value, Decimal):
        return format(parse_inr(value), ".2f")
    if isinstance(value, dict):
        return {key: serialize_decimals(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_decimals(item) for item in value]
    return value


class SchemeService:
    def __init__(self, db: Session) -> None:
        self.analyses = FinancialRepository(db)

    def analyze(self, user: User, payload: SchemeAnalysisRequest) -> SchemeAnalysisResponse:
        analysis = self.analyses.get_owned(payload.financial_analysis_id, user.id)
        if analysis is None:
            raise HTTPException(status_code=404, detail="Financial analysis not found.")
        # Explicit supported version: do not accept future formulas by changing a global version constant.
        if analysis.analysis_version != "financial-v1" or FINANCIAL_ANALYSIS_VERSION != "financial-v1":
            raise HTTPException(status_code=409, detail={"code": "unsupported_financial_version", "message": "This financial analysis version cannot be interpreted. Recalculate your financial structure."})
        try:
            fields = ("available_margin_capital", "beneficiary_contribution", "feasible_project_cost", "indicative_loan_amount")
            for field in fields:
                value = getattr(analysis, field)
                if not isinstance(value, Decimal) or not value.is_finite() or value != parse_inr(value) or value <= 0:
                    raise ValueError("Invalid stored amount.")
            if analysis.available_margin_capital > MAXIMUM_MARGIN_INPUT:
                raise ValueError("Margin outside supported input range.")
            expected = calculate_structure(analysis.available_margin_capital)
            if any(getattr(analysis, field) != expected[field] for field in fields):
                raise ValueError("Stored structure differs from its source margin.")
            business = FinancialBusiness.model_validate(analysis.result_snapshot["business"])
            if business.id != analysis.business_profile_id:
                raise ValueError("Business snapshot identity mismatch.")
            result = evaluate_scheme(analysis.feasible_project_cost, analysis.beneficiary_contribution, analysis.indicative_loan_amount)
        except (ValueError, TypeError, KeyError, ArithmeticError) as exc:
            raise HTTPException(status_code=409, detail={"code": "inconsistent_financial_snapshot", "message": "The saved financial structure is inconsistent. Recalculate your financial structure."}) from exc
        return SchemeAnalysisResponse.model_validate({
            "financial_analysis_id": analysis.id,
            "financial_analysis_version": analysis.analysis_version,
            "business": business,
            **serialize_decimals(result),
        })
