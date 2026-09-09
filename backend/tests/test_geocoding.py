import time

import httpx
import pytest

from app.core.config import Settings
from app.engines.nearby_market_engine import location_fingerprint, normalize_location
from app.providers.errors import ProviderError
from app.providers.geocoding import NominatimProvider
from app.services.geocoding_service import acceptable_candidate

LOCATION = {"village": "Mankoli", "taluka": "Bhiwandi", "district": "Thane", "state": "Maharashtra", "pincode": "421302"}


def candidate(**overrides):
    return {"lat": "19.25", "lon": "73.02", "display_name": "Mankoli, Thane, Maharashtra, India", "addresstype": "village",
            "address": {"village": "Mankoli", "county": "Thane", "state": "Maharashtra", "country_code": "in"}, **overrides}


def provider(handler):
    return NominatimProvider(Settings(), httpx.Client(transport=httpx.MockTransport(handler)))


def test_success_and_minimal_query():
    def handler(request):
        assert request.url.params["countrycodes"] == "in"
        assert request.url.params["addressdetails"] == "1"
        assert "UdyamMitra" in request.headers["User-Agent"]
        assert "authorization" not in request.headers
        return httpx.Response(200, json=[candidate()])
    result = provider(handler).search("Mankoli, Bhiwandi, Thane, Maharashtra, India", time.monotonic() + 10)[0]
    assert result["latitude"] == 19.25
    assert result["precision"] == "village"
    assert "confidence" not in result
    assert acceptable_candidate(result, LOCATION) == "RESOLVED"


@pytest.mark.parametrize("raw", [{}, [candidate(lat="nan")], [candidate(lon="999")], [candidate(address=None)], [candidate(display_name=None)]])
def test_malformed_provider_response(raw):
    with pytest.raises(ProviderError):
        provider(lambda request: httpx.Response(200, json=raw)).search("locality", time.monotonic() + 10)


def test_timeout():
    def timeout(request):
        raise httpx.ReadTimeout("private query must not appear in public error")
    with pytest.raises(ProviderError) as error:
        provider(timeout).search("private locality", time.monotonic() + 10)
    assert error.value.code == "PROVIDER_TIMEOUT"
    assert error.value.status == 504
    assert "private" not in str(error.value)


def test_throttle():
    with pytest.raises(ProviderError) as error:
        provider(lambda request: httpx.Response(429, headers={"Retry-After": "12"})).search("locality", time.monotonic() + 10)
    assert error.value.status == 429
    assert error.value.retry_after == 12


@pytest.mark.parametrize(("address", "precision", "expected"), [
    ({"village": "Mankoli", "county": "Thane", "state": "Maharashtra", "country_code": "us"}, "village", "REJECTED"),
    ({"village": "Mankoli", "county": "Thane", "state": "Gujarat", "country_code": "in"}, "village", "REJECTED"),
    ({"village": "Mankoli", "county": "Pune", "state": "Maharashtra", "country_code": "in"}, "village", "REJECTED"),
    ({"county": "Thane", "state": "Maharashtra", "country_code": "in"}, "county", "AMBIGUOUS"),
])
def test_conservative_context(address, precision, expected):
    assert acceptable_candidate({"address": address, "precision": precision}, LOCATION) == expected


def test_unicode_and_changed_fingerprint():
    assert normalize_location("  माणकोली  ") == "माणकोली"
    assert location_fingerprint(LOCATION) == location_fingerprint({**LOCATION, "village": " MANKOLI "})
    assert location_fingerprint(LOCATION) != location_fingerprint({**LOCATION, "village": "Other"})
    assert location_fingerprint({**LOCATION, "village": "माणकोली"}) != location_fingerprint({**LOCATION, "village": "वाघोली"})


@pytest.mark.parametrize("overrides", [
    {"geocoding_min_interval_seconds": 0.5},
    {"osm_user_agent": "User-Agent\r\nInjected: true"},
    {"overpass_query_timeout_seconds": 25, "overpass_timeout_seconds": 25},
    {"nearby_request_timeout_seconds": 56},
    {"overpass_max_elements": 0},
    {"nominatim_base_url": "file:///private/file"},
])
def test_configuration_guards(overrides):
    with pytest.raises(ValueError):
        Settings(**overrides)
