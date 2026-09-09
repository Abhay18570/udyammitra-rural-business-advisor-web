"""Conservative interpretation: broad legacy aliases never become confirmed assets."""
from app.feasibility_rules import SKILL_ALIASES, RESOURCE_ALIASES
from app.engines.nearby_market_engine import normalize_location
from app.schemas.business_analysis import RequirementMatch


def match_requirements(declared, required, kind):
    aliases = SKILL_ALIASES if kind == 'skills' else RESOURCE_ALIASES
    result = []
    for requirement in required:
        target = normalize_location(requirement)
        exact = next((value for value in declared if normalize_location(value) == target), None)
        tentative = next((value for value in declared if target in {normalize_location(v) for v in aliases.get(normalize_location(value), set())}), None)
        result.append(RequirementMatch(requirement=requirement,
            status='CONFIRMED_SELF_REPORTED' if exact else 'TENTATIVE_ALIAS_MATCH' if tentative else 'NOT_RECORDED',
            declared_value=exact or tentative))
    return result
