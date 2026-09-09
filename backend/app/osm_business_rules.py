"""Conservative OSM evidence rules. Retail outlets do not prove production/repair."""
from dataclasses import dataclass
from typing import Tuple

MAPPING_VERSION = "osm-business-v1"
INNER_RADIUS_METERS = 5000
OUTER_RADIUS_METERS = 10000
CANDIDATE_RADIUS_METERS = 10100


@dataclass(frozen=True)
class TagRule:
    code: str
    classification: str
    tags: Tuple[Tuple[str, str], ...]


def direct(code, **tags):
    return TagRule(code, "DIRECT_COMPETITOR", tuple(tags.items()))


def related(code, **tags):
    return TagRule(code, "RELATED_BUSINESS", tuple(tags.items()))


BUSINESS_RULES = {
    "tailoring-alteration": (
        direct("TAILOR_SHOP", shop="tailor"), direct("TAILOR_CRAFT", craft="tailor"),
        direct("DRESSMAKER", craft="dressmaker"), related("CLOTHING_RETAIL", shop="clothes")),
    "mobile-repair-accessories": (
        direct("EXPLICIT_PHONE_REPAIR", **{"shop": "mobile_phone", "mobile_phone:repair": "yes"}),
        direct("PHONE_REPAIR_CRAFT", craft="electronics_repair", electronics_repair="phone"),
        related("PHONE_RETAIL", shop="mobile_phone")),
    "kirana-general-store": (
        direct("CONVENIENCE_STORE", shop="convenience"), direct("GENERAL_STORE", shop="general"),
        related("SUPERMARKET", shop="supermarket"), related("GROCERY_SPECIALIST", shop="grocery")),
    "dairy-enterprise": (
        direct("MILK_PRODUCING_FARM", landuse="farmyard", produce="milk"),
        related("DAIRY_RETAIL", shop="dairy"), related("DAIRY_PROCESSOR", industrial="dairy")),
    "poultry-enterprise": (
        direct("EGG_PRODUCING_FARM", landuse="farmyard", produce="eggs"),
        direct("POULTRY_PRODUCING_FARM", landuse="farmyard", produce="poultry"),
        related("POULTRY_RETAIL", shop="butcher", butcher="poultry")),
    "flour-mill": (
        direct("FLOUR_PRODUCTION", man_made="works", product="flour"),
        direct("FLOUR_MILL_CRAFT", craft="mill", product="flour"),
        related("UNSPECIFIED_MILL", craft="mill")),
    "food-processing-unit": (
        related("FOOD_PROCESSOR", industrial="food"),
        related("SPICE_PRODUCER", man_made="works", product="spices"),
        related("PICKLE_PRODUCER", man_made="works", product="pickles")),
    "agri-equipment-rental": (
        direct("AGRICULTURAL_MACHINERY_RENTAL", **{"shop": "agrarian", "agrarian": "machinery", "rental": "yes"}),
        related("AGRICULTURAL_MACHINERY_SUPPLIER", shop="agrarian", agrarian="machinery")),
}
WEAK_MAPPING_BUSINESSES = frozenset({"dairy-enterprise", "poultry-enterprise", "flour-mill", "food-processing-unit", "agri-equipment-rental"})
