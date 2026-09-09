import pytest

from app.engines.nearby_market_engine import match_business, radius_band
from app.osm_business_rules import BUSINESS_RULES


@pytest.mark.parametrize(("distance", "expected"), [(0, "WITHIN_5_KM"), (5000, "WITHIN_5_KM"), (5000.00001, "BETWEEN_5_AND_10_KM"), (10000, "BETWEEN_5_AND_10_KM"), (10000.00001, None)])
def test_radius_boundary_before_rounding(distance, expected):
    assert radius_band(distance) == expected


@pytest.mark.parametrize("distance", [-1, float("nan"), float("inf")])
def test_invalid_distance(distance):
    with pytest.raises(ValueError):
        radius_band(distance)


@pytest.mark.parametrize(("slug", "tags", "classification"), [
    ("tailoring-alteration", {"shop": "tailor"}, "DIRECT_COMPETITOR"),
    ("tailoring-alteration", {"craft": "tailor"}, "DIRECT_COMPETITOR"),
    ("tailoring-alteration", {"shop": "clothes"}, "RELATED_BUSINESS"),
    ("tailoring-alteration", {"shop": "convenience"}, None),
    ("tailoring-alteration", {"shop": "tailor", "disused": "yes"}, None),
    ("tailoring-alteration", {"shop": "tailor", "abandoned:shop": "tailor"}, None),
    ("mobile-repair-accessories", {"shop": "mobile_phone"}, "RELATED_BUSINESS"),
    ("mobile-repair-accessories", {"shop": "mobile_phone", "mobile_phone:repair": "yes"}, "DIRECT_COMPETITOR"),
    ("mobile-repair-accessories", {"craft": "electronics_repair", "electronics_repair": "phone"}, "DIRECT_COMPETITOR"),
    ("kirana-general-store", {"shop": "general"}, "DIRECT_COMPETITOR"),
    ("kirana-general-store", {"shop": "supermarket"}, "RELATED_BUSINESS"),
    ("dairy-enterprise", {"shop": "dairy"}, "RELATED_BUSINESS"),
    ("dairy-enterprise", {"landuse": "farmyard", "produce": "milk;eggs"}, "DIRECT_COMPETITOR"),
    ("poultry-enterprise", {"landuse": "farmyard"}, None),
    ("poultry-enterprise", {"landuse": "farmyard", "produce": "eggs"}, "DIRECT_COMPETITOR"),
    ("flour-mill", {"man_made": "watermill"}, None),
    ("flour-mill", {"man_made": "works", "product": "flour"}, "DIRECT_COMPETITOR"),
    ("food-processing-unit", {"industrial": "food"}, "RELATED_BUSINESS"),
    ("food-processing-unit", {"landuse": "industrial"}, None),
    ("agri-equipment-rental", {"shop": "agrarian", "agrarian": "machinery"}, "RELATED_BUSINESS"),
    ("agri-equipment-rental", {"shop": "agrarian", "agrarian": "machinery", "rental": "yes"}, "DIRECT_COMPETITOR"),
])
def test_mapping_evidence(slug, tags, classification):
    result = match_business(slug, tags)
    assert (result["classification"] if result else None) == classification
    if result:
        assert result["matching_rule"] and result["matching_evidence"]


def test_catalog_coverage_and_unknown_mapping():
    assert len(BUSINESS_RULES) == 8
    with pytest.raises(ValueError):
        match_business("not-supported", {"shop": "tailor"})
