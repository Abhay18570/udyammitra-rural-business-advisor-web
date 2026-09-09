"""Conservative Nearby Search (New) Table A mappings; never infer activities from names.

Verified against https://developers.google.com/maps/documentation/places/web-service/place-types
"""
from dataclasses import dataclass

MAPPING_VERSION = 'google-types-20260908-v1'


@dataclass(frozen=True)
class PlaceRule:
    direct: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    limited: bool = True

    @property
    def included_types(self):
        return self.direct + self.related


BUSINESS_RULES = {
    'tailoring-alteration': PlaceRule(('tailor',), ('clothing_store',), False),
    # Selling phones/electronics does not establish repair capability.
    'mobile-repair-accessories': PlaceRule(related=('cell_phone_store', 'electronics_store')),
    'kirana-general-store': PlaceRule(('convenience_store', 'grocery_store'), ('supermarket',), False),
    # Food retail and butchers are related outlets, never production competitors.
    'dairy-enterprise': PlaceRule(related=('food_store',)),
    'poultry-enterprise': PlaceRule(related=('butcher_shop',)),
    'flour-mill': PlaceRule(),
    'food-processing-unit': PlaceRule(),
    'agri-equipment-rental': PlaceRule(),
}


def match_place(slug, tags):
    rule = BUSINESS_RULES[slug]
    types = set(tags.get('types', '').split(';')) | {tags.get('primary_type', '')}
    classification, matches = 'GENERIC_POI', []
    for role, allowed in [('DIRECT_COMPETITOR', rule.direct), ('RELATED_BUSINESS', rule.related)]:
        matches = sorted(types.intersection(allowed))
        if matches:
            classification = role
            break
    return {'classification': classification, 'matched_business_slug': slug,
            'matching_rule': f'{MAPPING_VERSION}:{slug}:{classification}',
            'matching_evidence': [{'key': 'google_place_type', 'value': value} for value in matches]}
