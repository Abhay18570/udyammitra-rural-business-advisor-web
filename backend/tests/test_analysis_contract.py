import uuid

import pytest
from pydantic import ValidationError

from app.schemas.analysis import AnalysisInput


def valid_input() -> dict:
    return {
        "location": {"state": "Maharashtra", "district": "Pune", "block": "Haveli", "village": "Wagholi", "pincode": "412207"},
        "available_margin_capital": "100000.00",
        "proposed_business_id": str(uuid.uuid4()),
        "proposed_business_category": "SERVICES",
        "radius_km": 5,
        "enterprise_stage": "NEW",
        "currency": "INR",
    }


def test_analysis_contract_accepts_documented_input() -> None:
    parsed = AnalysisInput.model_validate(valid_input())
    assert parsed.available_margin_capital.as_tuple().exponent == -2
    assert parsed.radius_km.value == 5


@pytest.mark.parametrize(("field", "value"), [("radius_km", 7), ("currency", "USD"), ("enterprise_stage", "PLANNING")])
def test_analysis_contract_rejects_values_outside_domain(field: str, value) -> None:
    payload = valid_input()
    payload[field] = value
    with pytest.raises(ValidationError):
        AnalysisInput.model_validate(payload)


def test_scheme_shared_vocabulary_is_backward_compatible() -> None:
    from app.schemas.analysis import SchemeStatus, SchemeType
    assert {item.value for item in SchemeStatus} == {
        "ELIGIBLE", "INELIGIBLE", "VERIFICATION_REQUIRED", "ELIGIBLE_WITH_GAP", "OUT_OF_SUPPORTED_RANGE",
    }
    assert {item.value for item in SchemeType} == {"MICRO_FINANCE", "TERM_LOAN"}
