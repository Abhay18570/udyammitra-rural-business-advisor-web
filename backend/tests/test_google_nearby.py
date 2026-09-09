import json
import uuid

import httpx
import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.models.market_cache import NearbyQueryCache
from app.models.market_poi import MarketPOI
from app.providers.http import DeadlineClient
from app.repositories.nearby_market_repository import NearbyMarketRepository, utcnow
from app.services import nearby_market_service
from app.utils.spatial import geography_point
from tests.test_google_places import place
from tests.test_nearby_market import setup_user, nearby, expire
from tests.test_geocoding import candidate


@pytest.fixture
def google(monkeypatch):
    settings = get_settings().model_copy(update={'nearby_market_provider': 'google'})
    monkeypatch.setattr(nearby_market_service, 'get_settings', lambda: settings)
    state = {'requests': [], 'status': 200, 'places': [place(), place('related', 'clothing_store'),
             place('outside', location={'latitude': 20, 'longitude': 73}), place('generic', 'restaurant')]}
    def handler(request):
        state['requests'].append(request)
        if 'nominatim' in request.url.host:
            return httpx.Response(200, json=[candidate(lat='19', lon='73')])
        if 'overpass' in request.url.host:
            return httpx.Response(200, json={'elements': []})
        if state['status'] != 200:
            return httpx.Response(state['status'], text='private failure')
        return httpx.Response(200, json={'places': state['places']})
    monkeypatch.setattr(nearby_market_service, 'DeadlineClient', lambda: DeadlineClient(transport=httpx.MockTransport(handler)))
    state['settings'] = settings
    return state


def test_google_cache_postgis_and_provenance(client, db_session, google):
    token = setup_user(client)
    response = nearby(client, token, radius_km=5)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['source']['provider'] == 'GOOGLE_PLACES'
    assert body['summary']['direct_competitors'] == 1
    assert body['summary']['related_businesses'] == 1
    assert body['summary']['nearest_direct_competitor']['external_id'] == 'ChIJ-mock'
    assert len(body['generic_pois']) == 1
    assert all(p['distance_meters'] <= 5000 for p in body['competitors']+body['related_businesses'])
    assert 'outside' not in [p['external_id'] for p in body['competitors']]
    assert 'GOOGLE_RANKED_SUBSET' in {w['code'] for w in body['quality']['warnings']}
    assert body['quality']['attribution'] == 'Google Maps'
    assert nearby(client, token, radius_km=5).json()['source']['mode'] == 'LIVE'
    assert len(google['requests']) == 3
    assert db_session.scalar(select(NearbyQueryCache.provider).where(NearbyQueryCache.provider == 'GOOGLE_PLACES')) is None
    assert db_session.scalar(select(MarketPOI.external_id).where(MarketPOI.name == 'Example business').limit(1)) is None
    assert 'mock-backend-key' not in response.text
    assert 'X-Goog' not in response.text


def test_provider_and_radius_cache_isolation(client, db_session, google):
    token = setup_user(client)
    for radius in (1, 5, 10):
        body = nearby(client, token, radius_km=radius).json()
        assert body['source']['mode'] == 'LIVE'
        assert nearby(client, token, radius_km=radius).json()['source']['mode'] == 'LIVE'
    google['settings'].nearby_market_provider = 'overpass'
    body = nearby(client, token, radius_km=5).json()
    assert body['source']['provider'] == 'OPENSTREETMAP_OVERPASS'
    assert body['source']['mode'] == 'LIVE' and body['summary']['direct_competitors'] == 0
    assert set(db_session.scalars(select(NearbyQueryCache.provider))) == {'OPENSTREETMAP'}
    google['settings'].nearby_market_provider = 'google'
    assert nearby(client, token, radius_km=5).json()['source']['mode'] == 'LIVE'


@pytest.mark.parametrize('failure', ['http', 'partial'])
def test_google_failure_does_not_reuse_content_or_switch_provider(client, db_session, google, failure):
    token = setup_user(client)
    assert nearby(client, token).status_code == 200
    expire(db_session)
    if failure == 'http':
        google['status'] = 503
    else:
        google['places'].append({'id': 'malformed'})
    response = nearby(client, token)
    assert response.status_code == 503
    assert not any('overpass' in r.url.host for r in google['requests'])


@pytest.mark.parametrize('old_cache', [False, True])
def test_failure_without_valid_cache(client, db_session, google, old_cache):
    token = setup_user(client)
    if old_cache:
        assert nearby(client, token).status_code == 200
        expire(db_session, age=8*86400)
    google['status'] = 403
    response = nearby(client, token)
    assert response.status_code == 503
    assert 'private' not in response.text
    assert not any('overpass' in r.url.host for r in google['requests'])


def test_missing_key_endpoint_and_empty(client, google):
    token = setup_user(client)
    google['settings'].google_places_api_key = None
    response = nearby(client, token)
    assert response.status_code == 503
    assert response.json()['detail']['code'] == 'PROVIDER_NOT_CONFIGURED'
    from pydantic import SecretStr
    google['settings'].google_places_api_key = SecretStr('mock-backend-key')
    google['places'] = []
    body = nearby(client, token).json()
    assert body['summary']['direct_competitors'] == 0
    assert body['summary']['nearest_direct_competitor'] is None
    assert 'NO_MAPPED_DIRECT_COMPETITORS' in {w['code'] for w in body['quality']['warnings']}


@pytest.mark.parametrize('radius', [1, 5, 10])
def test_google_exact_boundary_and_cross_provider_id(db_session, radius):
    ids = []
    for index, meters in enumerate([radius*1000, radius*1000+0.01]):
        row = MarketPOI(id=uuid.uuid4(), provider='GOOGLE_PLACES', external_type='place', external_id=f'ChIJ-boundary-{index}',
            name='Boundary', geo_point=func.ST_Project(geography_point(19,73), meters,0.0), coordinate_kind='PLACE_LOCATION',
            normalized_tags={}, normalized_address={}, fetched_at=utcnow())
        db_session.add(row)
        ids.append(row.id)
    db_session.flush()
    results = NearbyMarketRepository(db_session).spatial_pois(ids, {'latitude':19,'longitude':73}, radius*1000)
    assert len(results) == 1 and results[0]['distance_meters'] == radius*1000


def test_google_saved_business_analysis(client, db_session, google):
    from tests.test_business_analysis import prepare, run
    from tests.test_feasibility import auth
    token, financial_id = prepare(client, db_session)
    response = run(client, token, financial_id)
    assert response.status_code == 409
    assert response.json()['detail']['code'] == 'GOOGLE_HISTORY_UNAVAILABLE'
    from app.models.business_analysis import BusinessAnalysis
    assert db_session.scalar(select(func.count()).select_from(BusinessAnalysis)) == 0


def test_provider_identity_constraint(db_session):
    for provider in ('OPENSTREETMAP', 'GOOGLE_PLACES'):
        db_session.add(MarketPOI(id=uuid.uuid4(), provider=provider, external_type='place', external_id='123456789',
            name='Shared identifier', geo_point=geography_point(19,73), coordinate_kind='PLACE_LOCATION',
            normalized_tags={}, normalized_address={}, fetched_at=utcnow()))
    db_session.flush()
    assert db_session.scalar(select(func.count()).select_from(MarketPOI).where(MarketPOI.external_id=='123456789')) == 2


def test_id_migration_preserves_numeric_ids_and_accepts_google_ids(db_session, monkeypatch):
    import importlib.util
    from pathlib import Path
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import text
    # A temporary table shadows the real table only for this connection.
    db_session.execute(text('CREATE TEMP TABLE market_pois (external_id bigint NOT NULL) ON COMMIT DROP'))
    db_session.execute(text('INSERT INTO market_pois VALUES (9223372036854775807)'))
    file = Path(__file__).parents[1] / 'alembic/versions/20260908_10_provider_place_ids.py'
    spec = importlib.util.spec_from_file_location('place_id_migration', file)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    monkeypatch.setattr(migration, 'op', Operations(MigrationContext.configure(db_session.connection())))
    migration.upgrade()
    assert db_session.scalar(text('SELECT external_id FROM market_pois')) == '9223372036854775807'
    db_session.execute(text("INSERT INTO market_pois VALUES ('ChIJ-migration-example')"))
    assert db_session.scalar(text('SELECT count(*) FROM market_pois')) == 2
    db_session.execute(text("DELETE FROM market_pois WHERE external_id = 'ChIJ-migration-example'"))
    migration.downgrade()
    assert db_session.scalar(text('SELECT external_id FROM market_pois')) == 9223372036854775807
    db_session.execute(text('DROP TABLE pg_temp.market_pois'))
