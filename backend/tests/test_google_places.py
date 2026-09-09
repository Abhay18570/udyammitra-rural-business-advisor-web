import json
import time

import httpx
import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.providers.errors import ProviderError
from app.providers.google_places import GooglePlacesProvider, FIELD_MASK, build_payload, normalize_places
from app.providers.nearby import ProviderPolicy
from app.providers.overpass import OverpassProvider
from app.google_places_rules import BUSINESS_RULES, match_place


def settings(**kwargs):
    return Settings(_env_file=None, google_places_api_key='mock-backend-key', **kwargs)


def place(identity='ChIJ-mock', kind='tailor', **extra):
    return {'id': identity, 'displayName': {'text': 'Example business'}, 'location': {'latitude': 19, 'longitude': 73},
            'primaryType': kind, 'types': [kind, 'establishment'], 'formattedAddress': 'Example locality',
            'businessStatus': 'OPERATIONAL', **extra}


def test_default_and_selection():
    assert settings().nearby_market_provider == 'overpass'
    assert isinstance(ProviderPolicy(settings()).provider(None), OverpassProvider)
    assert isinstance(ProviderPolicy(settings(nearby_market_provider='google')).provider(None), GooglePlacesProvider)
    with pytest.raises(ValidationError):
        settings(nearby_market_provider='unknown')
    for count in (0, 21):
        with pytest.raises(ValidationError):
            settings(google_places_max_results=count)
    with pytest.raises(ValidationError):
        settings(google_places_base_url='https://example.org/collect')


@pytest.mark.parametrize('radius', [1000, 5000, 10000])
def test_request(radius):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={'places': [place()]})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        pois, rejected = GooglePlacesProvider(settings(), client).fetch('tailoring-alteration', 19, 73, time.monotonic()+10, radius)
    request = requests[0]
    assert str(request.url) == 'https://places.googleapis.com/v1/places:searchNearby'
    assert request.headers['X-Goog-Api-Key'] == 'mock-backend-key'
    assert request.headers['X-Goog-FieldMask'] == FIELD_MASK
    assert request.headers['Content-Type'] == 'application/json'
    assert 'mock-backend-key' not in str(request.url) + request.content.decode()
    payload = json.loads(request.content)
    assert payload == {'includedTypes': ['tailor', 'clothing_store'], 'maxResultCount': 20, 'rankPreference': 'DISTANCE',
                       'locationRestriction': {'circle': {'center': {'latitude': 19, 'longitude': 73}, 'radius': radius}}}
    assert len(FIELD_MASK.split(',')) == 7
    assert not any(word in FIELD_MASK.lower() for word in ('rating', 'review', 'photo', 'opening'))
    assert len(pois) == 1 and rejected == 0
    assert pois[0]['provider'] == 'GOOGLE_PLACES'
    assert pois[0]['external_type'] == 'place'
    assert pois[0]['external_id'] == 'ChIJ-mock'
    assert pois[0]['normalized_address'] == {'formatted_address': 'Example locality'}
    assert pois[0]['normalized_tags']['classification'] == 'DIRECT_COMPETITOR'


def test_missing_key_is_controlled():
    provider = GooglePlacesProvider(Settings(_env_file=None, google_places_api_key=None), None)
    with pytest.raises(ProviderError) as error:
        provider.fetch('tailoring-alteration', 19, 73, time.monotonic()+10, 5000)
    assert error.value.code == 'PROVIDER_NOT_CONFIGURED'
    assert 'mock-backend-key' not in repr(settings())


@pytest.mark.parametrize('status', [400, 401, 403, 429, 500, 503, 302])
def test_upstream_errors_sanitized(status):
    with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(status, text='private upstream diagnostics'))) as client:
        with pytest.raises(ProviderError) as error:
            GooglePlacesProvider(settings(), client).fetch('tailoring-alteration', 19, 73, time.monotonic()+10, 5000)
    assert error.value.status == (429 if status == 429 else 503)
    assert 'private' not in str(error.value)


def test_timeout():
    def fail(request):
        raise httpx.ReadTimeout('private details')
    with httpx.Client(transport=httpx.MockTransport(fail)) as client:
        with pytest.raises(ProviderError) as error:
            GooglePlacesProvider(settings(), client).fetch('tailoring-alteration', 19, 73, time.monotonic()+10, 5000)
    assert error.value.code == 'PROVIDER_TIMEOUT'


@pytest.mark.parametrize('raw', [[], {'places': None}, {'error': {}}, {'places': [place(location={'latitude': True,'longitude':73})]}, {'places': [place(location={'latitude': 91,'longitude':73})]}, {'places': [place(displayName=None)]}, {'places': [place(businessStatus='UNKNOWN')]}])
def test_malformed(raw):
    with pytest.raises(ProviderError):
        normalize_places(raw, 'tailoring-alteration', 20)


def test_normalization_closed_duplicates_generic_and_no_raw():
    raw = [place(reviews=['never persist']), place(), place('closed', businessStatus='CLOSED_PERMANENTLY'),
           place('temporary', businessStatus='CLOSED_TEMPORARILY'), place('related', 'clothing_store'), place('generic', 'restaurant')]
    pois, rejected = normalize_places({'places':raw}, 'tailoring-alteration', 20)
    assert rejected == 0 and len(pois) == 3
    assert [p['normalized_tags']['classification'] for p in pois] == ['DIRECT_COMPETITOR', 'RELATED_BUSINESS', 'GENERIC_POI']
    assert 'reviews' not in json.dumps(pois)
    assert normalize_places({}, 'tailoring-alteration', 20) == ([], 0)
    assert normalize_places({'places': []}, 'tailoring-alteration', 20) == ([], 0)
    with pytest.raises(ProviderError):
        normalize_places({'places': [place(), place('other')]}, 'tailoring-alteration', 1)


@pytest.mark.parametrize('slug', list(BUSINESS_RULES))
def test_mapping_registry_and_coverage(slug):
    rule = BUSINESS_RULES[slug]
    policy = ProviderPolicy(settings(nearby_market_provider='google'))
    warnings = {w['code'] for w in policy.warnings(slug)}
    assert 'GOOGLE_RANKED_SUBSET' in warnings
    assert ('LIMITED_BUSINESS_MAPPING' in warnings) == rule.limited
    for kind in rule.direct:
        assert match_place(slug, {'types': kind})['classification'] == 'DIRECT_COMPETITOR'
    for kind in rule.related:
        assert match_place(slug, {'types': kind})['classification'] == 'RELATED_BUSINESS'
    if not rule.included_types:
        assert 'NO_SUPPORTED_NEARBY_TYPES' in warnings
        assert GooglePlacesProvider(settings(), None).fetch(slug, 19, 73, time.monotonic()+10, 5000) == ([], 0)


def test_cache_identity():
    location = {'latitude': 19, 'longitude': 73, 'location_fingerprint': 'locality-v1'}
    osm, google = ProviderPolicy(settings()), ProviderPolicy(settings(nearby_market_provider='google'))
    key = google.cache_key('tailoring-alteration', location, 5000)
    assert key != osm.cache_key('tailoring-alteration', location, 5000)
    assert key != google.cache_key('tailoring-alteration', location, 1000)
    assert key != google.cache_key('tailoring-alteration', {**location, 'location_fingerprint': 'changed'}, 5000)
    assert key != ProviderPolicy(settings(nearby_market_provider='google', google_places_max_results=10)).cache_key('tailoring-alteration', location, 5000)
    google.mapping_version = 'new-version'
    assert key != google.cache_key('tailoring-alteration', location, 5000)
