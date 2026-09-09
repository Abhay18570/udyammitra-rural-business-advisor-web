import time

import httpx
import pytest

from app.core.config import Settings
from app.providers.errors import ProviderError
from app.providers.overpass import OverpassProvider, build_query, normalize_elements


def node(external_id=1, **overrides):
    return {"type": "node", "id": external_id, "lat": 19.0, "lon": 73.0, "tags": {"shop": "tailor", "name": "Local Tailor"}, **overrides}


def test_node_way_relation_duplicates_and_missing_name():
    elements = [node(), node(), node(tags={"craft": "tailor"}),
                {"type": "way", "id": 1, "center": {"lat": 19, "lon": 73}, "tags": {"shop": "tailor"}},
                {"type": "relation", "id": 1, "center": {"lat": 19, "lon": 73}, "tags": {"shop": "tailor"}}]
    pois, rejected = normalize_elements({"elements": elements}, 100)
    assert len(pois) == 3 and rejected == 0
    assert all(item["external_id"] == "1" for item in pois)
    assert pois[1]["name"] == "Unnamed mapped business"
    assert pois[0]["coordinate_kind"] == "NODE"
    assert pois[1]["coordinate_kind"] == pois[2]["coordinate_kind"] == "REPRESENTATIVE_CENTER"


@pytest.mark.parametrize("element", [node(lat=91), node(lon="nan"), node(lat=True), node(tags=[]), {"type": "way", "id": 2}, node(external_id=True)])
def test_invalid_record_count(element):
    pois, rejected = normalize_elements({"elements": [node(), element]}, 100)
    assert len(pois) == 1 and rejected == 1


@pytest.mark.parametrize("payload", [{"remark": "runtime error", "elements": []}, {}, {"elements": "bad"}, {"elements": [node(lat=91)]}])
def test_invalid_or_partial_payload(payload):
    with pytest.raises(ProviderError):
        normalize_elements(payload, 100)


def test_element_limit():
    with pytest.raises(ProviderError) as error:
        normalize_elements({"elements": [node(), node(2)]}, 1)
    assert error.value.code == "PROVIDER_TOO_MANY_ELEMENTS"


def test_size_limit_and_no_auth_forwarding():
    def handler(request):
        assert request.method == "POST"
        assert "authorization" not in request.headers
        assert "nwr" in request.content.decode()
        return httpx.Response(200, content=b" " * 2000)
    settings = Settings(overpass_max_response_bytes=1024)
    adapter = OverpassProvider(settings, httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(ProviderError) as error:
        adapter.fetch("tailoring-alteration", 19, 73, time.monotonic() + 10)
    assert error.value.code == "PROVIDER_RESPONSE_TOO_LARGE"


def test_query_is_backend_owned_and_bounded():
    query = build_query("tailoring-alteration", 19, 73, 20)
    assert "around:10100,19.0000000,73.0000000" in query
    assert '"shop"' in query and '"craft"' in query
    assert "out center tags" in query
    with pytest.raises(ValueError):
        build_query('tailor];out;', 19, 73, 20)


def test_connection_retry_is_bounded():
    calls = []
    def fail(request):
        calls.append(request)
        raise httpx.ConnectError("private host")
    adapter = OverpassProvider(Settings(), httpx.Client(transport=httpx.MockTransport(fail)))
    with pytest.raises(ProviderError) as error:
        adapter.fetch("tailoring-alteration", 19, 73, time.monotonic() + 10)
    assert error.value.code == "PROVIDER_UNAVAILABLE"
    assert len(calls) == 2


def test_rate_limit_is_not_retried():
    calls = []
    def throttle(request):
        calls.append(request)
        return httpx.Response(429, headers={"Retry-After": "30"})
    adapter = OverpassProvider(Settings(), httpx.Client(transport=httpx.MockTransport(throttle)))
    with pytest.raises(ProviderError) as error:
        adapter.fetch("tailoring-alteration", 19, 73, time.monotonic() + 10)
    assert error.value.status == 429 and error.value.retry_after == 30
    assert len(calls) == 1


def test_real_transport_cancels_at_total_deadline():
    import asyncio
    from app.providers.http import DeadlineClient
    async def slow(request):
        await asyncio.sleep(0.2)
        return httpx.Response(200, json={"elements": []})
    adapter = OverpassProvider(Settings(), DeadlineClient(httpx.MockTransport(slow)))
    with pytest.raises(ProviderError) as error:
        adapter.fetch("tailoring-alteration", 19, 73, time.monotonic() + 0.01)
    assert error.value.code == "PROVIDER_TIMEOUT"
