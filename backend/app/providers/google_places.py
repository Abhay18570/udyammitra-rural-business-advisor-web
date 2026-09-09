"""Server-only Google Places API (New), with bounded transport and no raw response persistence."""
import math

from app.business_query_rules import normalize_query, classify_query, VERSION

from app.google_places_rules import BUSINESS_RULES, MAPPING_VERSION, match_place
from app.providers.errors import ProviderError
from app.providers.http import request_json

FIELD_MASK = 'places.id,places.displayName,places.location,places.primaryType,places.types,places.formattedAddress,places.businessStatus'


def validate_search_area(latitude, longitude, radius_meters, max_results):
    if type(radius_meters) is not int or not 1000 <= radius_meters <= 10000:
        raise ValueError('Invalid radius')
    if not math.isfinite(latitude) or not math.isfinite(longitude) or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError('Invalid coordinates')
    if type(max_results) is not int or not 1 <= max_results <= 20:
        raise ValueError('Invalid result limit')


def build_payload(slug, latitude, longitude, radius_meters, max_results):
    validate_search_area(latitude, longitude, radius_meters, max_results)
    rule = BUSINESS_RULES[slug]
    return {'includedTypes': list(rule.included_types), 'maxResultCount': max_results, 'rankPreference': 'DISTANCE',
            'locationRestriction': {'circle': {'center': {'latitude': latitude, 'longitude': longitude}, 'radius': radius_meters}}}


def normalize_places(raw, slug, max_results, business_query=None):
    # Protobuf JSON represents an empty repeated places field as {}.
    if not isinstance(raw, dict) or 'error' in raw or (raw and 'places' not in raw) or not isinstance(raw.get('places', []), list):
        raise ProviderError('PROVIDER_INVALID_RESPONSE')
    places = raw.get('places', [])
    if len(places) > max_results:
        raise ProviderError('PROVIDER_TOO_MANY_ELEMENTS')
    pois, seen, rejected = [], set(), 0
    for place in places:
        try:
            if not isinstance(place, dict):
                raise ValueError()
            status = place.get('businessStatus')
            if status in {'CLOSED_TEMPORARILY', 'CLOSED_PERMANENTLY'}:
                continue
            if status != 'OPERATIONAL':
                raise ValueError()
            identity = place['id']
            if not isinstance(identity, str) or not identity or len(identity) > 255:
                raise ValueError()
            lat, lon = place['location']['latitude'], place['location']['longitude']
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in (lat, lon)) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                raise ValueError()
            types, primary = place.get('types', []), place.get('primaryType', '')
            if not isinstance(types, list) or len(types) > 100 or any(not isinstance(t, str) or len(t) > 100 or ';' in t for t in types):
                raise ValueError()
            name = place.get('displayName', {}).get('text', 'Unnamed mapped business')
            address = place.get('formattedAddress', '')
            if any(not isinstance(v, str) or len(v) > 2000 for v in (primary, name, address)):
                raise ValueError()
            tags = {'primary_type': primary, 'types': ';'.join(types), 'business_status': status, 'mapping_version': VERSION if business_query else MAPPING_VERSION}
            match = classify_query(business_query, name, tags, slug or "") if business_query else match_place(slug, tags)
            tags['classification'] = match['classification']
            if identity in seen:
                continue
            seen.add(identity)
            pois.append({'provider': 'GOOGLE_PLACES', 'external_type': 'place', 'external_id': identity,
                         'name': name or 'Unnamed mapped business', 'latitude': lat, 'longitude': lon,
                         'coordinate_kind': 'PLACE_LOCATION', 'normalized_tags': tags,
                         'normalized_address': {'formatted_address': address}})
        except (KeyError, TypeError, ValueError, AttributeError):
            rejected += 1
    if rejected and not pois:
        raise ProviderError('PROVIDER_INVALID_RESPONSE')
    return pois, rejected


class GooglePlacesProvider:
    def __init__(self, settings, client):
        self.settings, self.client = settings, client

    def fetch_text(self, query, latitude, longitude, deadline, radius_meters=10000):
        return fetch_text(self, query, latitude, longitude, deadline, radius_meters)

    def fetch(self, slug, latitude, longitude, deadline, radius_meters=10000):
        secret = self.settings.google_places_api_key
        if not secret or not secret.get_secret_value().strip():
            raise ProviderError('PROVIDER_NOT_CONFIGURED', 503)
        payload = build_payload(slug, latitude, longitude, radius_meters, self.settings.google_places_max_results)
        # No unfiltered search for unsupported production/rental categories.
        if not payload['includedTypes']:
            return [], 0
        raw = request_json(self.client, 'POST', str(self.settings.google_places_base_url), deadline=deadline,
                           timeout=self.settings.google_places_timeout_seconds, max_bytes=1_000_000,
                           json=payload, headers={'X-Goog-Api-Key': secret.get_secret_value(),
                                                'X-Goog-FieldMask': FIELD_MASK, 'Content-Type': 'application/json'})
        return normalize_places(raw, slug, self.settings.google_places_max_results)


TEXT_FIELD_MASK = FIELD_MASK + ',nextPageToken'


def build_text_payload(query, latitude, longitude, radius_meters, page_size):
    validate_search_area(latitude, longitude, radius_meters, page_size)
    query = normalize_query(query)
    if not 2 <= len(query) <= 200:
        raise ValueError('Invalid business query')
    return {'textQuery': query, 'pageSize': page_size,
            'locationBias': {'circle': {'center': {'latitude': latitude, 'longitude': longitude}, 'radius': radius_meters}}}


def fetch_text(provider, query, latitude, longitude, deadline, radius_meters):
    settings = provider.settings
    secret = settings.google_places_api_key
    if not secret or not secret.get_secret_value().strip():
        raise ProviderError('PROVIDER_NOT_CONFIGURED', 503)
    payload = build_text_payload(query, latitude, longitude, radius_meters, settings.google_places_max_results)
    pois, seen, tokens, rejected = [], set(), set(), 0
    for _ in range(settings.google_places_text_max_pages):
        raw = request_json(provider.client, 'POST', str(settings.google_places_text_search_url), deadline=deadline,
                           timeout=settings.google_places_timeout_seconds, max_bytes=1_000_000,
                           json=payload, headers={'X-Goog-Api-Key': secret.get_secret_value(),
                                                 'X-Goog-FieldMask': TEXT_FIELD_MASK, 'Content-Type': 'application/json'})
        if not isinstance(raw, dict):
            raise ProviderError('PROVIDER_INVALID_RESPONSE')
        token = raw.get('nextPageToken', '')
        if not isinstance(token, str) or len(token) > 10000 or (token and token in tokens):
            raise ProviderError('PROVIDER_INVALID_RESPONSE')
        page, bad = normalize_places(raw, None, settings.google_places_max_results, business_query=query)
        rejected += bad
        for poi in page:
            if poi['external_id'] not in seen:
                seen.add(poi['external_id'])
                pois.append(poi)
        if not token:
            break
        tokens.add(token)
        payload = {**payload, 'pageToken': token}
    return pois, rejected
