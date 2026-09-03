import re
from decimal import Decimal, ROUND_HALF_UP

from app.feasibility_rules import CAPITAL_RANGE_BOUNDARIES, FEASIBILITY_THRESHOLDS, RESOURCE_ALIASES, SKILL_ALIASES, VIABILITY_WEIGHTS, feasibility_label

HUNDRED = Decimal("100")


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _expanded(values, aliases):
    output = set()
    for value in values:
        normalized = _key(value)
        output.add(normalized)
        output.update(_key(item) for item in aliases.get(normalized, set()))
    return output


def _round_score(value: Decimal) -> int:
    return max(0, min(100, int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))))


def calculate_weighted_score(scores: dict[str, int]) -> tuple[int, list[dict]]:
    titles = {"LOCAL_DEMAND": "Local Demand", "COMPETITION_OPPORTUNITY": "Competition Opportunity", "SKILL_MATCH": "Skill Match", "FINANCIAL_FIT": "Financial Fit", "MARKET_ACCESS": "Market Access", "SUPPLY_CHAIN": "Supply Chain"}
    components, total = [], Decimal("0")
    for code, weight in VIABILITY_WEIGHTS.items():
        score = max(0, min(100, int(scores[code])))
        contribution = (Decimal(score) * weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total += contribution
        components.append({"code": code, "title": titles[code], "score": score, "weight": str(weight), "weighted_contribution": str(contribution)})
    return _round_score(total), components


def skill_match(user_skills: list[str], required: list[str], preferred: list[str]) -> dict:
    available = _expanded(user_skills, SKILL_ALIASES)
    matched_required = [item for item in required if _key(item) in available]
    missing_required = [item for item in required if _key(item) not in available]
    matched_preferred = [item for item in preferred if _key(item) in available]
    required_ratio = Decimal(len(matched_required)) / Decimal(len(required)) if required else Decimal("1")
    preferred_ratio = Decimal(len(matched_preferred)) / Decimal(len(preferred)) if preferred else Decimal("1")
    score = _round_score(required_ratio * Decimal("70") + preferred_ratio * Decimal("30"))
    return {"matched_required_skills": matched_required, "missing_required_skills": missing_required, "matched_preferred_skills": matched_preferred, "skill_match_score": score}


def resource_readiness(user_resources: list[str], required: list[str], optional: list[str]) -> dict:
    available = _expanded(user_resources, RESOURCE_ALIASES)
    matched_required = [item for item in required if _key(item) in available]
    missing_required = [item for item in required if _key(item) not in available]
    matched_optional = [item for item in optional if _key(item) in available]
    required_ratio = Decimal(len(matched_required)) / Decimal(len(required)) if required else Decimal("1")
    optional_ratio = Decimal(len(matched_optional)) / Decimal(len(optional)) if optional else Decimal("1")
    score = _round_score(required_ratio * Decimal("80") + optional_ratio * Decimal("20"))
    return {"available_required_resources": matched_required, "missing_required_resources": missing_required, "available_optional_resources": matched_optional, "resource_readiness_score": score}


def _range_affordability(capital_range, requirement: Decimal) -> Decimal:
    lower, upper = CAPITAL_RANGE_BOUNDARIES[capital_range]
    if upper is None:
        return min(HUNDRED, lower / requirement * HUNDRED)
    if lower >= requirement:
        return HUNDRED
    if upper < requirement:
        return upper / requirement * HUNDRED
    # The requirement falls inside the declared range. Range position gives 75–100,
    # without pretending that the user owns its maximum value.
    position = (upper - requirement) / (upper - lower) if upper > lower else Decimal("0")
    return Decimal("75") + position * Decimal("25")


def financial_fit(profile, business, resource_score: int) -> tuple[int, str, bool]:
    requirement = max(Decimal(business.minimum_capital), Decimal(business.estimated_setup_cost_min) + Decimal(business.working_capital_min))
    if profile.own_capital is not None:
        capital = max(Decimal("0"), Decimal(profile.own_capital))
        affordability = min(HUNDRED, capital / requirement * HUNDRED)
        source = "exact own capital"
    elif profile.capital_range is not None:
        affordability = _range_affordability(profile.capital_range, requirement)
        source = "selected capital range"
    else:
        affordability = Decimal("0")
        source = "missing capital information"
    score = _round_score(affordability * Decimal("0.80") + Decimal(resource_score) * Decimal("0.20"))
    financing_needed = affordability < HUNDRED
    if affordability >= HUNDRED:
        explanation = f"Your {source} meets the minimum practical planning requirement; existing resources are considered without assigning them a rupee value."
    elif affordability >= Decimal("75"):
        explanation = f"Your {source} is close to the minimum practical planning requirement. Financing may be required."
    else:
        explanation = f"Your {source} is below the typical minimum setup and working-capital range. Financing may be required."
    return score, explanation, financing_needed


def _current_business(profile, business) -> bool:
    existing = profile.existing_business
    if not profile.has_existing_business or not existing:
        return False
    source = _key(f"{existing.business_name} {existing.business_category}")
    candidates = {_key(business.name), _key(business.slug), _key(business.category.value)}
    aliases = {
        "tailoring-alteration": {"tailoring", "alteration"}, "mobile-repair-accessories": {"mobile repair", "electronics repair"},
        "kirana-general-store": {"kirana", "general store", "retail"}, "dairy-enterprise": {"dairy", "milk"},
        "poultry-enterprise": {"poultry", "chicken", "egg"}, "flour-mill": {"flour mill", "atta chakki"},
        "food-processing-unit": {"food processing"}, "agri-equipment-rental": {"equipment rental", "agricultural equipment"},
    }
    candidates.update(aliases.get(business.slug, set()))
    return any(candidate and candidate in source for candidate in candidates)


def evaluate_business(profile, business, market: dict) -> dict:
    skills = skill_match([item.name for item in profile.skills], business.required_skills, business.preferred_skills)
    resources = resource_readiness([item.name for item in profile.resources], business.required_resources, business.optional_resources)
    financial_score, capital_explanation, financing_needed = financial_fit(profile, business, resources["resource_readiness_score"])
    scores = {"LOCAL_DEMAND": market["demand_score"], "COMPETITION_OPPORTUNITY": market["competition_opportunity_score"], "SKILL_MATCH": skills["skill_match_score"], "FINANCIAL_FIT": financial_score, "MARKET_ACCESS": market["market_access_score"], "SUPPLY_CHAIN": market["supply_chain_score"]}
    final_score, components = calculate_weighted_score(scores)
    strengths = []
    strength_rules = [("LOCAL_DEMAND", "STRONG_LOCAL_DEMAND", "Strong local demand", "The saved market snapshot shows a strong local demand signal."), ("COMPETITION_OPPORTUNITY", "LOW_COMPETITION", "Competition opportunity", "The saved evidence indicates room to differentiate or serve unmet demand."), ("SKILL_MATCH", "STRONG_SKILL_MATCH", "Strong skill match", "Your selected skills align with this business profile."), ("FINANCIAL_FIT", "GOOD_CAPITAL_FIT", "Good capital fit", "Your capital and resource readiness align relatively well with the planning range."), ("MARKET_ACCESS", "STRONG_MARKET_ACCESS", "Strong market access", "Nearby access signals support reaching customers or channels."), ("SUPPLY_CHAIN", "STRONG_SUPPLY_CHAIN", "Strong supply chain", "The saved market snapshot shows supportive supply-chain access.")]
    for factor, code, title, explanation in strength_rules:
        if scores[factor] >= 70:
            strengths.append({"code": code, "title": title, "explanation": explanation})
    gaps = []
    if skills["missing_required_skills"]: gaps.append({"code": "MISSING_REQUIRED_SKILLS", "severity": "HIGH" if skills["skill_match_score"] < 40 else "MEDIUM", "explanation": "Develop the listed required skills before investing."})
    if resources["missing_required_resources"]: gaps.append({"code": "MISSING_REQUIRED_RESOURCES", "severity": "MEDIUM", "explanation": "Some required operating resources are not present in your profile."})
    if scores["COMPETITION_OPPORTUNITY"] < 45: gaps.append({"code": "HIGH_COMPETITION", "severity": "HIGH", "explanation": "The saved market snapshot indicates substantial local competition."})
    if scores["FINANCIAL_FIT"] < 50: gaps.append({"code": "CAPITAL_GAP", "severity": "HIGH", "explanation": capital_explanation})
    if scores["MARKET_ACCESS"] < 45: gaps.append({"code": "WEAK_MARKET_ACCESS", "severity": "MEDIUM", "explanation": "Nearby market and transport access signals are limited."})
    if scores["SUPPLY_CHAIN"] < 45: gaps.append({"code": "SUPPLY_CHAIN_RISK", "severity": "MEDIUM", "explanation": "Confirm supplier availability and transport access before proceeding."})
    actions = []
    if skills["missing_required_skills"]: actions.append("Develop the missing required skills before investing.")
    if resources["missing_required_resources"]: actions.append("Confirm access to the missing required resources.")
    if financing_needed: actions.append("Review financing requirements before proceeding.")
    if scores["COMPETITION_OPPORTUNITY"] < 45: actions.append("Study differentiation and underserved customer segments.")
    if scores["SUPPLY_CHAIN"] < 45: actions.append("Confirm supplier and transport access.")
    if not actions: actions.append("Validate assumptions with prospective customers before investing.")
    return {"rank": 0, "business_id": str(business.id), "business_slug": business.slug, "business_name": business.name, "business_category": business.category.value, "short_description": business.short_description, "final_feasibility_score": final_score, "feasibility_label": feasibility_label(final_score), "is_current_business": _current_business(profile, business), "components": components, "skills": skills, "resources": resources, "capital_fit_explanation": capital_explanation, "financing_may_be_required": financing_needed, "strengths": strengths, "gaps": gaps, "next_actions": actions, "market_threats": market.get("localized_threats", [])}


def rank_results(results: list[dict]) -> list[dict]:
    def component(result, code):
        return next(item["score"] for item in result["components"] if item["code"] == code)
    ranked = sorted(results, key=lambda item: (-item["final_feasibility_score"], -component(item, "LOCAL_DEMAND"), -component(item, "SKILL_MATCH"), item["business_name"].casefold(), item["business_slug"]))
    for rank, item in enumerate(ranked, 1): item["rank"] = rank
    return ranked
