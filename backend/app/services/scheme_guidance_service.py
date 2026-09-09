"""Read-only source selection. All money/routing comes from existing engines."""
from dataclasses import asdict

from app.engines.financial_engine import calculate_structure
from app.engines.scheme_engine import evaluate_scheme
from app.financial_rules import BENEFICIARY_MARGIN_RATE, LOAN_SHARE_RATE, MAXIMUM_MARGIN_INPUT
from app.repositories.financial_repository import FinancialRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.scheme import SchemeAnalysisRequest, SchemeGuidanceResponse
from app.scheme_rules import SCHEMES
from app.services.scheme_service import SchemeService, serialize_decimals
from app.utils.money import parse_inr


class SchemeGuidanceService:
    def __init__(self, db):
        self.db = db

    def guidance(self, user):
        response = {
            'source': 'FINANCIAL_PLAN_REQUIRED',
            'rules': serialize_decimals([asdict(rule) for rule in SCHEMES]),
            'funding_share_percent': str(LOAN_SHARE_RATE * 100),
            'contribution_share_percent': str(BENEFICIARY_MARGIN_RATE * 100),
        }
        saved = FinancialRepository(self.db).latest(user.id)
        if saved is not None:
            # A corrupt/unavailable saved plan must never silently become an estimate.
            result = SchemeService(self.db).analyze(user, SchemeAnalysisRequest(financial_analysis_id=saved.id))
            response.update(source='SAVED_FINANCIAL_PLAN', result=result.model_dump(),
                            setup_funding_gap=format(parse_inr(saved.funding_gap), '.2f'),
                            source_observed_at=saved.created_at.isoformat())
        else:
            profile = ProfileRepository(self.db).get_for_user(user)
            if profile is not None and profile.own_capital is not None:
                try:
                    margin = parse_inr(profile.own_capital)
                    if margin <= 0 or margin > MAXIMUM_MARGIN_INPUT:
                        raise ValueError('Unusable contribution')
                    structure = calculate_structure(margin)
                    result = evaluate_scheme(structure['feasible_project_cost'], structure['beneficiary_contribution'], structure['indicative_loan_amount'])
                    response.update(source='PROFILE_ILLUSTRATION', result=serialize_decimals(result),
                                    source_observed_at=profile.updated_at.isoformat())
                except (ValueError, TypeError, ArithmeticError):
                    response['notice'] = 'CONTRIBUTION_UNUSABLE'
        return SchemeGuidanceResponse.model_validate(response)
