"""Provider selection and downstream matching; HTTP stays in concrete providers."""
from typing import Protocol

from app.engines.nearby_market_engine import fingerprint, match_business
from app.osm_business_rules import MAPPING_VERSION as OSM_VERSION, WEAK_MAPPING_BUSINESSES
from app.google_places_rules import BUSINESS_RULES, MAPPING_VERSION as GOOGLE_VERSION, match_place
from app.business_query_rules import VERSION
from app.providers.google_places import build_text_payload, TEXT_FIELD_MASK, GooglePlacesProvider, build_payload, FIELD_MASK
from app.providers.overpass import OverpassProvider, build_query


class NearbyBusinessProvider(Protocol):
    def fetch(self, slug: str, latitude: float, longitude: float, deadline: float, radius_meters: int = 10000) -> tuple[list[dict], int]: ...


class ProviderPolicy:
    def __init__(self, settings):
        self.settings = settings
        self.google = settings.nearby_market_provider == 'google'
        self.name = 'google' if self.google else 'overpass'
        self.storage_provider = 'GOOGLE_PLACES' if self.google else 'OPENSTREETMAP'
        self.source_provider = 'GOOGLE_PLACES' if self.google else 'OPENSTREETMAP_OVERPASS'
        self.mapping_version = GOOGLE_VERSION if self.google else OSM_VERSION
        self.attribution = 'Google Maps' if self.google else '© OpenStreetMap contributors (ODbL)'

    def provider(self, client) -> NearbyBusinessProvider:
        return (GooglePlacesProvider if self.google else OverpassProvider)(self.settings, client)

    def cache_key(self, slug, location, radius):
        s = self.settings
        query = build_payload(slug, location['latitude'], location['longitude'], radius, s.google_places_max_results) if self.google else build_query(slug, location['latitude'], location['longitude'], s.overpass_query_timeout_seconds, radius)
        return fingerprint({'provider': self.storage_provider, 'endpoint': str(s.google_places_base_url if self.google else s.overpass_base_url),
                            'location': [location['latitude'], location['longitude']], 'location_fingerprint': location['location_fingerprint'],
                            'business': slug, 'radius': radius, 'mapping_version': self.mapping_version,
                            'query': query, 'query_version': 'selected-radius-providers-v1', 'fields': FIELD_MASK if self.google else None})

    def text_request_key(self, query, location, radius):
        return fingerprint({'provider': self.storage_provider, 'endpoint': str(self.settings.google_places_text_search_url),
                            'query': build_text_payload(query, location['latitude'], location['longitude'], radius, self.settings.google_places_max_results),
                            'location_fingerprint': location['location_fingerprint'], 'mapping_version': VERSION,
                            'fields': TEXT_FIELD_MASK, 'pages': self.settings.google_places_text_max_pages})

    def match(self, slug, tags):
        return (match_place if self.google else match_business)(slug, tags)

    def warnings(self, slug):
        if not self.google:
            warnings = [{'code': 'OSM_COVERAGE_LIMITED', 'message': 'OpenStreetMap coverage varies. Mapped records are not a complete establishment census; distances are from the resolved locality centre, not your premises.'}]
            if slug in WEAK_MAPPING_BUSINESSES:
                warnings.append({'code': 'LIMITED_BUSINESS_MAPPING', 'message': 'OSM tags for this production/rental activity are limited. Related outlets or facilities do not prove direct competition.'})
            return warnings
        warnings = [{'code': 'GOOGLE_RANKED_SUBSET', 'message': f'Google Places returns a ranked subset of at most {self.settings.google_places_max_results} nearby establishments. Mapped counts and density are not a complete census; distances are from the resolved locality centre.'}]
        rule = BUSINESS_RULES[slug]
        if rule.limited:
            warnings.append({'code': 'LIMITED_BUSINESS_MAPPING', 'message': 'Google structured types do not establish direct competition for this activity. Related outlets do not prove production, repair or rental capability.'})
        if not rule.included_types:
            warnings.append({'code': 'NO_SUPPORTED_NEARBY_TYPES', 'message': 'No defensible Nearby Search type mapping is configured for this business. No Google search was performed; empty evidence does not establish absence of competitors.'})
        return warnings
