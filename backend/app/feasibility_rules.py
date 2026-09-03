from decimal import Decimal

from app.models.profile import CapitalRange

BUSINESS_FEASIBILITY_VERSION = "feasibility-v1"
VIABILITY_WEIGHTS = {
    "LOCAL_DEMAND": Decimal("0.25"),
    "COMPETITION_OPPORTUNITY": Decimal("0.20"),
    "SKILL_MATCH": Decimal("0.20"),
    "FINANCIAL_FIT": Decimal("0.15"),
    "MARKET_ACCESS": Decimal("0.10"),
    "SUPPLY_CHAIN": Decimal("0.10"),
}
FEASIBILITY_THRESHOLDS = ((90, "VERY_STRONG"), (75, "STRONG"), (60, "GOOD"), (40, "MODERATE"), (0, "LOW"))
CAPITAL_RANGE_BOUNDARIES = {
    CapitalRange.UP_TO_50000: (Decimal("0"), Decimal("50000")),
    CapitalRange.RANGE_50000_TO_100000: (Decimal("50000"), Decimal("100000")),
    CapitalRange.RANGE_100000_TO_250000: (Decimal("100000"), Decimal("250000")),
    CapitalRange.RANGE_250000_TO_500000: (Decimal("250000"), Decimal("500000")),
    CapitalRange.RANGE_500000_TO_1000000: (Decimal("500000"), Decimal("1000000")),
    CapitalRange.ABOVE_1000000: (Decimal("1000000"), None),
}
SKILL_ALIASES = {
    "tailoring": {"basic stitching", "garment measurement", "pattern cutting", "embroidery"},
    "repairing": {"mobile repair basics", "electronics troubleshooting", "equipment maintenance", "basic maintenance"},
    "farming": {"livestock care", "feed management", "fodder planning", "bird care", "feed and water management", "farm equipment operation", "grain handling"},
    "dairy": {"livestock care", "clean milk handling", "feed management", "animal health observation", "fodder planning"},
    "cooking": {"food preparation", "food hygiene", "quality consistency", "recipe standardisation"},
    "retail": {"retail operations", "inventory management", "customer service", "supplier negotiation", "retail sales"},
    "machinery": {"machine operation", "farm equipment operation", "equipment maintenance", "basic maintenance"},
    "computer": {"digital payments", "basic bookkeeping", "record keeping", "cost record keeping"},
    "food processing": {"food preparation", "food hygiene", "quality consistency", "packaging and labelling", "recipe standardisation"},
    "driving": {"driving", "transport access"},
}
RESOURCE_ALIASES = {
    "land": {"own agricultural land", "own land", "own farm produce", "cattle shed", "ventilated poultry shed"},
    "shop": {"clean workspace", "small shop or workspace", "accessible shop space", "commercial workspace", "hygienic workspace", "shop frontage"},
    "vehicle": {"delivery vehicle", "own vehicle", "transport access"},
    "storage space": {"storage space", "secure storage", "dry storage", "feed storage", "secure equipment storage"},
    "machinery": {"chaff cutter", "three-phase power", "workshop space", "trained equipment operator"},
    "livestock": {"cattle shed", "ventilated poultry shed"},
    "electricity": {"reliable electricity", "electricity", "suitable electrical connection", "reliable water and electricity", "backup power", "three-phase power"},
    "water": {"reliable water", "reliable water and electricity"},
    "internet": {"internet access"},
}
DISCLAIMER = "Feasibility scores are decision-support indicators based on your profile and the current demonstration market dataset. They do not guarantee revenue, profitability, loan approval, scheme eligibility, or business success."


def feasibility_label(score: int) -> str:
    return next(label for minimum, label in FEASIBILITY_THRESHOLDS if score >= minimum)
