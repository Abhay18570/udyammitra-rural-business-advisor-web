import hashlib
import json
import math
import unicodedata

from app.osm_business_rules import BUSINESS_RULES, INNER_RADIUS_METERS, OUTER_RADIUS_METERS


def normalize_location(value):
    return " ".join(unicodedata.normalize("NFKC", value or "").casefold().split())


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def location_fingerprint(location):
    return fingerprint({key: normalize_location(location.get(key)) for key in ("village", "taluka", "district", "state", "pincode")})


def radius_band(distance):
    if not math.isfinite(distance) or distance < 0:
        raise ValueError("Invalid distance")
    if distance <= INNER_RADIUS_METERS:
        return "WITHIN_5_KM"
    if distance <= OUTER_RADIUS_METERS:
        return "BETWEEN_5_AND_10_KM"
    return None


def match_business(slug, tags):
    if slug not in BUSINESS_RULES:
        raise ValueError("Unsupported business mapping")
    if any(tags.get(key, "").lower() in {"yes", "true", "1"} for key in ("disused", "abandoned", "demolished", "construction")):
        return None
    if any(key.startswith(("disused:", "abandoned:", "demolished:", "construction:", "was:")) for key in tags):
        return None
    for rule in BUSINESS_RULES[slug]:
        if all(value in {part.strip() for part in tags.get(key, "").split(";")} for key, value in rule.tags):
            return {"classification": rule.classification, "matched_business_slug": slug,
                    "matching_rule": rule.code, "matching_evidence": [{"key": key, "value": value} for key, value in rule.tags]}
    return None
