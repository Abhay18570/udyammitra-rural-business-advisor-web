from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.main import app
from app.models.government_scheme import GovernmentScheme
from app.repositories.government_scheme_repository import GovernmentSchemeRepository
from tests.test_government_scheme_catalog import catalog_db  # isolated PostgreSQL schema fixture

BASE = '/api/v1/government-schemes'


@pytest.fixture
def api(catalog_db):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = [
        ('alpha', 'Alpha', 'CENTRAL', None, ['Agriculture, Rural & Environment'], 'DATASET_ONLY', True),
        ('beta', 'Beta', 'STATE', 'Maharashtra', ['Education & Learning'], 'DATASET_ONLY', True),
        ('gamma', 'Gamma', 'STATE', 'Odisha', ['Education & Learning'], 'VERIFIED', True),
        ('alpha-two', 'Alpha', 'STATE', 'Maharashtra', ['Agriculture, Rural & Environment'], 'STALE', True),
        ('hidden', 'Hidden', 'STATE', 'Gujarat', ['Hidden category'], 'OFFICIAL_SOURCE_LINKED', False),
    ]
    for index, (slug, name, level, state, categories, status, active) in enumerate(rows):
        catalog_db.add(GovernmentScheme(slug=slug, scheme_name=name, level=level, state=state, categories=categories,
            tags=['महिला', 'Farmer'], details=('orchard ' * (4 if slug == 'beta' else 1)) + 'योजना ₹500\n' + 'x' * 500,
            benefits='equipment benefit ₹100', eligibility='Resident horticulture eligibility',
            application_process='Apply online\nStep 2', documents_required='आधार, प्रमाणपत्र',
            source_type='DATASET', source_dataset='fixture.csv', verification_status=status, is_active=active,
            created_at=now + timedelta(days=index)))
    catalog_db.flush()
    app.dependency_overrides[get_db] = lambda: catalog_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_list_contract_and_pagination(api):
    response = api.get(BASE)
    assert response.status_code == 200
    data = response.json()
    assert (data['total'], data['page'], data['page_size'], data['total_pages']) == (4, 1, 20, 1)
    assert len(data['items']) == 4
    assert 'discovery data' in data['disclaimer']
    assert set(data['items'][0]) == {'slug','scheme_name','short_description','level','state','categories','tags','verification_status','source_type'}
    assert all(len(item['short_description']) <= 240 for item in data['items'])
    first = api.get(BASE, params={'page_size': 2}).json()
    second = api.get(BASE, params={'page_size': 2, 'page': 2}).json()
    assert first['total_pages'] == 2
    assert {i['slug'] for i in first['items']}.isdisjoint(i['slug'] for i in second['items'])
    assert api.get(BASE, params={'page': 99}).json()['items'] == []
    assert api.get(BASE, params={'page_size': 100}).status_code == 200


@pytest.mark.parametrize('params,slugs', [
    ({'level': 'CENTRAL'}, {'alpha'}),
    ({'level': 'STATE'}, {'beta','gamma','alpha-two'}),
    ({'state': '  maHARashtra '}, {'beta','alpha-two'}),
    ({'state': 'Orissa'}, {'gamma'}),
    ({'state': 'Imaginary'}, set()),
    ({'state': 'Maharashtra', 'level': 'CENTRAL'}, set()),
    ({'category': 'Education & Learning'}, {'beta','gamma'}),
    ({'category': 'Agriculture, Rural & Environment'}, {'alpha','alpha-two'}),
    ({'category': 'Agriculture'}, set()),
    ({'verification_status': 'DATASET_ONLY'}, {'alpha','beta'}),
    ({'verification_status': 'VERIFIED'}, {'gamma'}),
    ({'verification_status': 'STALE'}, {'alpha-two'}),
    ({'verification_status': 'OFFICIAL_SOURCE_LINKED'}, set()),
    ({'state': 'Maharashtra','level': 'STATE','category': 'Education & Learning','verification_status': 'DATASET_ONLY','search': 'orchard'}, {'beta'}),
])
def test_filters(api, params, slugs):
    data = api.get(BASE, params=params).json()
    assert {i['slug'] for i in data['items']} == slugs
    assert data['total'] == len(slugs)


@pytest.mark.parametrize('sort,slugs', [
    ('name_asc', ['alpha','alpha-two','beta','gamma']),
    ('name_desc', ['gamma','beta','alpha','alpha-two']),
    ('newest', ['alpha-two','gamma','beta','alpha']),
    ('oldest', ['alpha','beta','gamma','alpha-two']),
])
def test_sorting(api, sort, slugs):
    assert [i['slug'] for i in api.get(BASE, params={'sort':sort}).json()['items']] == slugs


@pytest.mark.parametrize('term,expected', [('orchard',4),('equipment',4),('horticulture',4),('Gamma',1),('zzzznonexistent',0),('the',0),('   ',4),('"; DROP TABLE government_schemes; --',0)])
def test_search(api, term, expected):
    response = api.get(BASE, params={'search':term})
    assert response.status_code == 200
    assert response.json()['total'] == expected
    if expected == 0:
        assert response.json()['total_pages'] == 0


def test_search_relevance_precedes_sort(api):
    for sort in ['name_asc','name_desc','newest','oldest']:
        items = api.get(BASE, params={'search':'orchard','sort':sort}).json()['items']
        assert items[0]['slug'] == 'beta'


@pytest.mark.parametrize('params', [
    {'page':0}, {'page':-1}, {'page':'abc'}, {'page':1.5}, {'page_size':0}, {'page_size':101},
    {'level':'central'}, {'verification_status':'APPROVED'}, {'sort':'details; DROP TABLE'},
    {'search':'x'*201}, {'state':'x'*101}, {'category':'x'*201},
])
def test_invalid_queries(api, params):
    assert api.get(BASE, params=params).status_code == 422


@pytest.mark.parametrize('slug,level,state', [('alpha','CENTRAL',None),('beta','STATE','Maharashtra')])
def test_detail_contract(api, catalog_db, slug, level, state):
    response = api.get(BASE+'/'+slug)
    assert response.status_code == 200
    data = response.json()
    record = catalog_db.scalar(select(GovernmentScheme).where(GovernmentScheme.slug == slug))
    for field in ('slug','scheme_name','details','benefits','eligibility','application_process','documents_required','categories','tags','source_dataset'):
        assert data[field] == getattr(record, field)
    assert data['level'] == level and data['state'] == state
    assert data['verification_status'] == 'DATASET_ONLY' and data['source_type'] == 'DATASET'
    assert data['is_active'] is True
    assert set(data) == {'slug','scheme_name','details','benefits','eligibility','application_process','documents_required','level','state','categories','tags','verification_status','source_type','source_dataset','is_active','created_at','updated_at','disclaimer'}


@pytest.mark.parametrize('slug', ['unknown','hidden'])
def test_unknown_and_inactive_detail(api, slug):
    response = api.get(BASE+'/'+slug)
    assert response.status_code == 404
    assert response.json() == {'detail':'Government scheme not found.'}


def test_filters_metadata(api):
    response = api.get(BASE+'/filters')
    assert response.status_code == 200
    data = response.json()
    assert data == {'levels':['CENTRAL','STATE'], 'states':['Maharashtra','Odisha'],
        'categories':['Agriculture, Rural & Environment','Education & Learning'],
        'verification_statuses':['DATASET_ONLY','STALE','VERIFIED']}
    for values in data.values():
        assert values == sorted(set(values)) and all(values)


@pytest.mark.parametrize('path,method', [('', 'list_schemes'),('/alpha','get_scheme_by_slug'),('/filters','get_filter_metadata')])
def test_database_errors_are_sanitized(api, monkeypatch, path, method):
    def fail(*args):
        raise SQLAlchemyError('private-diagnostic-marker')
    monkeypatch.setattr(GovernmentSchemeRepository, method, fail)
    response = api.get(BASE+path)
    assert response.status_code == 503
    assert 'private-diagnostic-marker' not in response.text
    assert response.json() == {'detail':'Government scheme catalog is temporarily unavailable.'}


def test_swagger_and_read_only(api):
    assert api.get('/docs').status_code == 200
    schema = api.get('/openapi.json').json()
    for path in [BASE, BASE+'/filters', BASE+'/{slug}']:
        assert set(schema['paths'][path]) == {'get'}
        assert not schema['paths'][path]['get'].get('security')
    assert 'discovery data' in schema['paths'][BASE]['get']['description']
    assert api.post(BASE, json={}).status_code == 405
    assert api.delete(BASE+'/alpha').status_code == 405
