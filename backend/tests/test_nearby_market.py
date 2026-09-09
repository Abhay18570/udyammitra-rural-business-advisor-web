from datetime import timedelta
from urllib.parse import parse_qs
import time

import httpx
import pytest
from sqlalchemy import func, select, text, update

from app.models.market_cache import GeocodingCache, NearbyQueryCache
from app.models.market_poi import MarketPOI
from app.models.market import DemoLocalBusiness, MarketAnalysis
from app.models.business import BusinessProfile
from app.repositories.nearby_market_repository import utcnow, NearbyMarketRepository
from app.services import nearby_market_service
from app.engines.nearby_market_engine import radius_band
from app.utils.spatial import geography_point
from app.providers.errors import ProviderError
from tests.test_feasibility import register, auth
from tests.test_market import profile
from tests.test_geocoding import candidate


@pytest.fixture
def osm(monkeypatch):
    state = {"requests": [], "geocoding": [candidate(lat="19", lon="73")], "elements": [
        {"type": "node", "id": 1, "lat": 19, "lon": 73, "tags": {"shop": "tailor", "name": "Tailor A"}},
        {"type": "way", "id": 1, "center": {"lat": 19.06, "lon": 73}, "tags": {"craft": "tailor", "name": "Tailor B"}},
        {"type": "relation", "id": 1, "center": {"lat": 19.02, "lon": 73}, "tags": {"shop": "clothes", "name": "Clothes"}},
        {"type": "node", "id": 2, "lat": 19.2, "lon": 73, "tags": {"shop": "tailor", "name": "Outside"}},
    ], "fail": False}
    def handler(request):
        state["requests"].append(request)
        if "nominatim" in request.url.host:
            if state.get("geocoder_fail"):
                return httpx.Response(503)
            data = state["geocoding"]
            if callable(data):
                data = data(request.url.params["q"])
            return httpx.Response(200, json=data)
        if state["fail"]:
            return httpx.Response(503, text="private failure information")
        return httpx.Response(200, json={"elements": state["elements"], **state.get("overpass_extra", {})})
    from app.providers.http import DeadlineClient
    monkeypatch.setattr(nearby_market_service, "DeadlineClient", lambda: DeadlineClient(transport=httpx.MockTransport(handler)))
    return state


def setup_user(client):
    token = register(client, "nearby")
    profile(client, token, village="Mankoli", taluka="Bhiwandi", district="Thane")
    return token


def nearby(client, token, **extra):
    return client.post("/api/v1/market/nearby", headers=auth(token), json={"business_slug": "tailoring-alteration", "radius_km": 10, **extra})


def expire(db, age=90000):
    db.execute(update(NearbyQueryCache).values(expires_at=utcnow() - timedelta(seconds=1), fetched_at=utcnow() - timedelta(seconds=age)))
    db.flush()
    db.expire_all()


def test_api_live_cache_counts_and_privacy(client, db_session, osm):
    token = setup_user(client)
    before = [db_session.scalar(select(func.count()).select_from(model)) for model in (DemoLocalBusiness, MarketAnalysis)]
    response = nearby(client, token)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"]["mode"] == "LIVE" and body["source"]["cache_status"] == "FRESH_FETCH"
    assert body["summary"]["related_businesses"] == 1
    assert body["summary"]["direct_competitors"] == 2
    assert body["summary"]["nearest_direct_competitor"]["name"] == "Tailor A"
    assert len(body["related_businesses"]) == 1
    assert body["quality"]["complete_query"] is True and body["quality"]["rejected_record_count"] == 0
    assert body["competitors"][0]["distance_km"] == "0.00"
    assert all(isinstance(poi["external_id"], str) for poi in body["competitors"])
    assert body["radius"] == {"selected_km": 10, "selected_meters": 10000, "distance_method": "POSTGIS_GEOGRAPHY_SPHEROID"}
    cached = nearby(client, token)
    assert cached.status_code == 200 and cached.json()["source"]["mode"] == "CACHE"
    assert cached.json()["competitors"] == body["competitors"]
    assert len(osm["requests"]) == 2
    geocode, overpass = osm["requests"]
    assert set(geocode.url.params) == {"q", "format", "countrycodes", "addressdetails", "limit"}
    assert geocode.url.params["q"] == "Mankoli, Bhiwandi, Thane, Maharashtra, India"
    assert set(parse_qs(overpass.content.decode())) == {"data"}
    for request in osm["requests"]:
        assert "authorization" not in request.headers
        assert token not in str(request.url) + request.content.decode()
        assert "email" not in str(request.url) + request.content.decode()
        assert "financial" not in request.content.decode()
    assert before == [db_session.scalar(select(func.count()).select_from(model)) for model in (DemoLocalBusiness, MarketAnalysis)]


def test_empty_search_is_cached(client, db_session, osm):
    osm["elements"] = []
    token = setup_user(client)
    body = nearby(client, token).json()
    assert body["summary"]["direct_competitors"] == 0 and body["summary"]["nearest_direct_competitor"] is None
    assert body["competitors"] == body["related_businesses"] == []
    assert any(item["code"] == "NO_MAPPED_DIRECT_COMPETITORS" for item in body["quality"]["warnings"])
    assert nearby(client, token).json()["source"]["mode"] == "CACHE"
    assert len(osm["requests"]) == 2
    row = db_session.scalar(select(NearbyQueryCache))
    assert row.poi_ids == [] and row.complete
    assert (row.expires_at - row.fetched_at).total_seconds() == 3600


@pytest.mark.parametrize("failure", ["unavailable", "partial", "remark"])
def test_failed_refresh_preserves_cache_and_returns_stale(client, db_session, osm, failure):
    token = setup_user(client)
    initial = nearby(client, token).json()
    expire(db_session)
    previous = db_session.scalar(select(NearbyQueryCache))
    ids, fetched = list(previous.poi_ids), previous.fetched_at
    if failure == "unavailable":
        osm["fail"] = True
    elif failure == "partial":
        osm["elements"].append({"type": "way", "id": 99})
    else:
        osm["overpass_extra"] = {"remark": "timeout: incomplete"}
    response = nearby(client, token)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"]["mode"] == "CACHE" and body["source"]["cache_status"] == "STALE_CACHE"
    assert body["competitors"] == initial["competitors"]
    db_session.expire_all()
    current = db_session.scalar(select(NearbyQueryCache))
    assert current.poi_ids == ids and current.fetched_at == fetched
    assert any(item["code"] == "STALE_CACHE" for item in body["quality"]["warnings"])


def test_refresh_replaces_membership_without_deleting_shared_pois(client, db_session, osm):
    token = setup_user(client)
    assert nearby(client, token).status_code == 200
    count = db_session.scalar(select(func.count()).select_from(MarketPOI))
    expire(db_session)
    osm["elements"] = []
    response = nearby(client, token)
    assert response.status_code == 200, response.text
    assert response.json()["source"]["mode"] == "LIVE" and response.json()["summary"]["direct_competitors"] == 0
    assert db_session.scalar(select(func.count()).select_from(MarketPOI)) == count
    assert nearby(client, token).json()["source"]["mode"] == "CACHE"


def test_mapping_version_invalidates_cache(client, db_session, osm, monkeypatch):
    token = setup_user(client)
    assert nearby(client, token).status_code == 200
    from app.providers import nearby as provider_policy
    monkeypatch.setattr(provider_policy, "OSM_VERSION", "osm-business-v2")
    body = nearby(client, token).json()
    assert body["source"]["mode"] == "LIVE" and body["source"]["mapping_version"] == "osm-business-v2"
    assert len(osm["requests"]) == 3


@pytest.mark.parametrize("old_cache", [False, True])
def test_unavailable_without_usable_cache_is_not_empty_success(client, db_session, osm, old_cache):
    token = setup_user(client)
    if old_cache:
        assert nearby(client, token).status_code == 200
        expire(db_session, age=604801)
    osm["fail"] = True
    response = nearby(client, token)
    assert response.status_code == 503
    assert "private failure" not in response.text
    assert response.json()["detail"]["code"] == "PROVIDER_UNAVAILABLE"


def test_auth_profile_and_business_validation(client, db_session, osm):
    assert client.post("/api/v1/market/nearby", json={"business_slug": "tailoring-alteration"}).status_code == 401
    token = register(client, "nearby-incomplete")
    response = nearby(client, token)
    assert response.status_code == 409 and response.json()["detail"]["code"] == "PROFILE_LOCATION_REQUIRED"
    assert nearby(client, token, business_slug="unknown").status_code == 404
    business = db_session.scalar(select(BusinessProfile).where(BusinessProfile.slug == "tailoring-alteration"))
    business.is_active = False
    db_session.flush()
    assert nearby(client, token).status_code == 404
    assert osm["requests"] == []


@pytest.mark.parametrize("field", ["latitude", "longitude", "radius_meters", "competitor_count", "distance_meters", "radius_band", "provider_url", "query", "tags", "location_token"])
def test_forbidden_client_fields(client, osm, field):
    token = setup_user(client)
    assert nearby(client, token, **{field: "fake"}).status_code == 422
    assert osm["requests"] == []


@pytest.mark.parametrize(("geocoding", "expected_status", "code"), [
    ([], 422, "LOCATION_NOT_RESOLVED"),
    ([candidate(), candidate(lat="19.26")], 409, "LOCATION_CONFIRMATION_REQUIRED"),
    ([candidate(addresstype="county", address={"county": "Thane", "state": "Maharashtra", "country_code": "in"})], 409, "LOCATION_CONFIRMATION_REQUIRED"),
    ([candidate(address={"village": "Mankoli", "state": "Maharashtra", "country_code": "us"})], 422, "LOCATION_NOT_RESOLVED"),
    ([candidate(address={"village": "Mankoli", "state": "Gujarat", "country_code": "in"})], 422, "LOCATION_NOT_RESOLVED"),
])
def test_location_resolution_states(client, db_session, osm, geocoding, expected_status, code):
    token = setup_user(client)
    osm["geocoding"] = geocoding
    response = nearby(client, token)
    assert response.status_code == expected_status, response.text
    assert response.json()["detail"]["code"] == code
    count = len(osm["requests"])
    assert nearby(client, token).status_code == expected_status and len(osm["requests"]) == count
    assert all("nominatim" in request.url.host for request in osm["requests"])


def test_fallback_unicode_and_changed_fingerprint(client, db_session, osm):
    token = setup_user(client)
    osm["geocoding"] = lambda query: [] if "Bhiwandi" in query else [candidate(lat="19", lon="73")]
    assert nearby(client, token).status_code == 200
    assert [request.url.params["q"] for request in osm["requests"] if "nominatim" in request.url.host] == ["Mankoli, Bhiwandi, Thane, Maharashtra, India", "Mankoli, Thane, Maharashtra, India"]
    profile(client, token, village="माणकोली", taluka="Bhiwandi", district="Thane")
    osm["geocoding"] = [candidate(lat="19", lon="73", address={"village": "माणकोली", "county": "Thane", "state": "Maharashtra", "country_code": "in"})]
    assert nearby(client, token).status_code == 200
    assert db_session.scalar(select(func.count()).select_from(GeocodingCache)) == 2
    assert any("माणकोली" in request.url.params.get("q", "") for request in osm["requests"])


@pytest.mark.parametrize(("meters", "band"), [(0, "WITHIN_5_KM"), (5000, "WITHIN_5_KM"), (5000.01, "BETWEEN_5_AND_10_KM"), (10000, "BETWEEN_5_AND_10_KM"), (10000.01, None)])
def test_postgis_boundaries_and_coordinate_order(db_session, meters, band):
    row = db_session.execute(text('''WITH p AS (SELECT ST_SetSRID(ST_MakePoint(73,19),4326)::geography AS origin),
      q AS (SELECT origin, ST_Project(origin, :meters, 0.0) AS target FROM p)
      SELECT ST_Distance(origin,target) AS distance, ST_DWithin(origin,target,10000) AS included,
             ST_X(origin::geometry) AS lon, ST_Y(origin::geometry) AS lat FROM q'''), {"meters": meters}).one()
    assert abs(row.distance - meters) < 0.000001
    assert radius_band(row.distance) == band
    assert row.included == (meters <= 10000)
    assert (row.lon, row.lat) == (73, 19)
    assert db_session.scalar(select(func.ST_AsText(geography_point(19, 73)))) == "POINT(73 19)"


def test_cache_schema_and_spatial_index(db_session):
    assert db_session.scalar(text("SELECT PostGIS_Version()"))
    assert "USING gist (geo_point)" in db_session.scalar(text("SELECT indexdef FROM pg_indexes WHERE indexname='ix_market_pois_geo_point' AND schemaname=current_schema()"))
    assert db_session.scalar(text("SELECT count(*) FROM pg_constraint WHERE conname='uq_market_poi_external' AND connamespace=current_schema()::regnamespace")) == 1
    columns = db_session.execute(text("SELECT type, srid FROM geography_columns WHERE f_table_schema=current_schema() AND f_table_name='market_pois' AND f_geography_column='geo_point'")).one()
    assert columns == ("Point", 4326)


def test_provider_slots_are_exclusive_and_released(db_session):
    repository = NearbyMarketRepository(db_session)
    lease = repository.acquire("test-provider", time.monotonic() + 10)
    with pytest.raises(ProviderError) as error:
        repository.acquire("test-provider", time.monotonic() + 10)
    assert error.value.status == 429
    repository.release(lease)
    second = repository.acquire("test-provider", time.monotonic() + 10)
    repository.release(second, cooldown=60)
    with pytest.raises(ProviderError):
        repository.acquire("test-provider", time.monotonic() + 10)


def test_partial_without_cache_never_saves_query(client, db_session, osm):
    token = setup_user(client)
    osm["elements"].append({"type": "way", "id": 99})
    response = nearby(client, token)
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "PROVIDER_PARTIAL_RESPONSE"
    assert db_session.scalar(select(func.count()).select_from(NearbyQueryCache)) == 0
    assert db_session.scalar(select(func.count()).select_from(MarketPOI)) == 0


def test_cached_pois_do_not_prove_query_coverage(client, db_session, osm):
    from sqlalchemy import delete
    token = setup_user(client)
    assert nearby(client, token).status_code == 200
    db_session.execute(delete(NearbyQueryCache))
    db_session.flush()
    assert db_session.scalar(select(func.count()).select_from(MarketPOI)) > 0
    osm["fail"] = True
    assert nearby(client, token).status_code == 503


def test_untrusted_profile_coordinates_are_not_used_or_overwritten(client, osm):
    token = setup_user(client)
    update_response = client.put('/api/v1/profile', headers=auth(token), json={"latitude": "0", "longitude": "0", "onboarding_step": 2})
    assert update_response.status_code == 200
    response = nearby(client, token)
    assert response.status_code == 200
    assert response.json()["location"]["latitude"] == 19
    saved = client.get('/api/v1/profile', headers=auth(token)).json()
    assert float(saved["latitude"]) == float(saved["longitude"]) == 0


def test_geocoder_outage_is_controlled(client, db_session, osm):
    token = setup_user(client)
    osm["geocoder_fail"] = True
    response = nearby(client, token)
    assert response.status_code == 503
    assert db_session.scalar(select(func.count()).select_from(GeocodingCache)) == 0


def test_registry_matches_actual_seeded_catalog(db_session):
    from app.osm_business_rules import BUSINESS_RULES
    assert set(db_session.scalars(select(BusinessProfile.slug))) == set(BUSINESS_RULES)


@pytest.mark.parametrize('radius', range(1, 11))
def test_selected_radius_api(client, osm, radius):
    token = setup_user(client)
    response = nearby(client, token, radius_km=radius)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['radius']['selected_km'] == radius
    assert body['radius']['selected_meters'] == radius * 1000
    assert all(p['distance_meters'] <= radius * 1000 for p in body['competitors'] + body['related_businesses'])
    assert body['summary']['direct_competitors'] == len(body['competitors'])
    assert body['summary']['related_businesses'] == len(body['related_businesses'])
    query = parse_qs(osm['requests'][-1].content.decode())['data'][0]
    assert 'around:{},'.format(radius * 1000 + 100) in query


@pytest.mark.parametrize('radius', [0, -1, 11, 1.5, 5.0, '5', True, None])
def test_invalid_selected_radius(client, osm, radius):
    token = setup_user(client)
    assert nearby(client, token, radius_km=radius).status_code == 422
    assert osm['requests'] == []


def test_radius_required(client, osm):
    token = setup_user(client)
    assert client.post('/api/v1/market/nearby', headers=auth(token), json={'business_slug': 'tailoring-alteration'}).status_code == 422


def test_exact_radius_cache_isolation(client, db_session, osm):
    token = setup_user(client)
    for radius in [3, 8, 2]:
        assert nearby(client, token, radius_km=radius).json()['source']['mode'] == 'LIVE'
        assert nearby(client, token, radius_km=radius).json()['source']['mode'] == 'CACHE'
    assert len(osm['requests']) == 4  # One geocode, three distinct Overpass searches.
    assert set(db_session.scalars(select(NearbyQueryCache.radius_meters))) == {3000, 8000, 2000}


@pytest.mark.parametrize('radius', [1, 5, 10])
def test_selected_postgis_repository_boundary(db_session, radius):
    import uuid
    origin = geography_point(19, 73)
    ids = []
    for index, meters in enumerate([radius * 1000, radius * 1000 + 0.01]):
        poi = MarketPOI(id=uuid.uuid4(), provider='OPENSTREETMAP', external_type='node', external_id=str(99000 + index),
            name='Boundary', geo_point=func.ST_Project(origin, meters, 0.0), coordinate_kind='NODE',
            normalized_tags={'shop': 'tailor'}, normalized_address={}, fetched_at=utcnow())
        db_session.add(poi)
        ids.append(poi.id)
    db_session.flush()
    rows = NearbyMarketRepository(db_session).spatial_pois(ids, {'latitude': 19, 'longitude': 73}, radius * 1000)
    assert len(rows) == 1
    assert rows[0]['external_id'] == '99000'
    assert rows[0]['distance_meters'] == radius * 1000


def test_manual_nearby_business_does_not_update_profile(client, db_session, osm):
    token = setup_user(client)
    chosen = db_session.scalar(select(BusinessProfile).where(BusinessProfile.slug == 'kirana-general-store'))
    assert client.put('/api/v1/profile', headers=auth(token), json={'proposed_business_id': str(chosen.id), 'onboarding_step': 3}).status_code == 200
    assert nearby(client, token, radius_km=5).status_code == 200
    assert client.get('/api/v1/profile', headers=auth(token)).json()['proposed_business_id'] == str(chosen.id)
