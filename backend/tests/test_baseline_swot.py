from copy import deepcopy
from pathlib import Path
import importlib.util
import uuid
import pytest
from sqlalchemy import select, text
from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.data.baseline_swot import BASELINE_SWOT
from app.data.business_seed import BUSINESS_SEEDS, seed_businesses, seed_baseline_swot
from app.engines.competitor_analysis_engine import analyze_competition
from app.engines.swot_engine import analyze_swot
from app.engines.threat_engine import analyze_threats
from app.engines.profile_evidence import match_requirements
from app.models.business import BusinessProfile
from app.models.business_analysis import BusinessAnalysis
from app.schemas.business_analysis import BusinessAnalysisResponse, SwotItem
from tests.test_business_analysis_engines import context
from tests.test_business_analysis import prepare, run
from tests.test_nearby_market import osm
from tests.test_feasibility import auth


def compose(c):
    competition = analyze_competition(c)
    return analyze_swot(c, competition, analyze_threats(c, competition))


@pytest.mark.parametrize('slug', list(BASELINE_SWOT))
def test_all_businesses_complete_baseline(slug):
    result = compose(context(slug=slug))
    assert set(BASELINE_SWOT) == {b['slug'] for b in BUSINESS_SEEDS}
    for rows in result.values():
        baseline = [i for i in rows if i.source_type == 'BUSINESS_BASELINE']
        assert len(baseline) == 4
        assert all(i.title and i.explanation and i.importance == 'LOW' for i in baseline)
        assert all(i.evidence_ids == ['catalog.baseline_swot'] and not i.finding_ids for i in baseline)
        assert all('unverified' in ' '.join(i.limitations) for i in baseline)


def test_kirana_content():
    result = compose(context(slug='kirana-general-store'))
    for quadrant, title in [('strengths','Recurring demand for daily essentials'),('weaknesses','Working-capital dependence'),('opportunities','Home delivery and digital ordering'),('threats','Online and quick-commerce competition')]:
        assert any(i.title == title for i in result[quadrant])
    assert any('where such services operate' in i.explanation for i in result['threats'])


def test_dynamic_evidence_and_order():
    c = context()
    c.entrepreneur.skills = match_requirements(['Tailoring'], ['Tailoring'], 'skills')
    c.financial.alignment.funding_gap = '10000.00'
    c.budget.consistency_status = 'DIFFERENT'
    result = compose(c)
    rules = {i.rule_id:i for rows in result.values() for i in rows}
    for code, source in [('declared-skills','PROFILE'),('setup-gap','FINANCIAL'),('budget-different','PROFILE'),('related-channels','MARKET')]:
        assert rules[code].source_type == source
    assert rules['related-channels'].evidence_ids == ['market.related']
    assert result['weaknesses'][0].importance == 'HIGH'
    assert result == compose(c)
    ids = [ref for rows in result.values() for i in rows for ref in i.finding_ids]
    assert len(ids) == len(set(ids))


def test_duplicate_suppression():
    c = deepcopy(context())
    item = c.business.catalog_snapshot['baseline_swot']['strengths'][0]
    c.business.catalog_snapshot['baseline_swot']['strengths'].append({**item,'id':'copy','title':item['title'].upper()+'!!!'})
    assert len([i for i in compose(c)['strengths'] if i.source_type == 'BUSINESS_BASELINE']) == 4


def test_legacy_without_baseline():
    c = deepcopy(context(related=0))
    c.business.catalog_snapshot.pop('baseline_swot')
    assert compose(c)['opportunities'] == []
    item = SwotItem(id='old',rule_id='old',category='strengths',title='Old',explanation='Old evidence',evidence_ids=['profile.skills'])
    assert item.source_type == 'DYNAMIC'


@pytest.mark.parametrize('slug', list(BASELINE_SWOT))
def test_saved_snapshot(client,db_session,osm,slug):
    token,fid = prepare(client,db_session,slug=slug)
    response = run(client,token,fid)
    assert response.status_code == 201
    body = response.json()
    for rows in body['swot'].values():
        assert len([i for i in rows if i['source_type']=='BUSINESS_BASELINE']) == 4
    evidence = next(e for e in body['evidence'] if e['id']=='catalog.baseline_swot')
    assert evidence['source_kind']=='BUSINESS_BASELINE' and evidence['is_assumption']
    assert evidence['radius_km'] is None and evidence['geography'] is None
    row = db_session.get(BusinessAnalysis,uuid.UUID(body['id']))
    assert row.evidence_snapshot['business']['catalog_snapshot']['baseline_swot']==BASELINE_SWOT[slug]
    assert row.rule_versions['swot']=='swot-v2'
    db_session.get(BusinessProfile,row.business_id).baseline_swot = {}
    db_session.flush()
    assert client.get('/api/v1/business-analysis/'+body['id'],headers=auth(token)).json()==body
    legacy=deepcopy(body)
    for quadrant,items in legacy['swot'].items():
        legacy['swot'][quadrant]=[i for i in items if i['source_type']!='BUSINESS_BASELINE']
        for i in legacy['swot'][quadrant]: i.pop('source_type')
    assert BusinessAnalysisResponse.model_validate(legacy).id==uuid.UUID(body['id'])


def test_seed_idempotence_preserves_manual_fields(db_session):
    seed_businesses(db_session)
    b=db_session.scalar(select(BusinessProfile).where(BusinessProfile.slug=='kirana-general-store'))
    b.name='Manually maintained name'; b.major_risks=['Manual risk']; b.is_active=False; b.baseline_swot={}
    db_session.flush()
    assert seed_baseline_swot(db_session)=={'updated':1,'unchanged':7,'missing':0}
    assert b.name=='Manually maintained name' and b.major_risks==['Manual risk'] and not b.is_active
    assert seed_baseline_swot(db_session)=={'updated':0,'unchanged':8,'missing':0}


def test_migration_roundtrip_transaction(db_session):
    path=Path(__file__).parents[1]/'alembic/versions/20260910_11_baseline_swot.py'
    spec=importlib.util.spec_from_file_location('baseline_migration',path)
    migration=importlib.util.module_from_spec(spec);spec.loader.exec_module(migration)
    nested=db_session.begin_nested()
    try:
        with Operations.context(MigrationContext.configure(db_session.connection())):
            migration.downgrade();migration.upgrade()
        assert db_session.scalar(text('SELECT count(*) FROM business_profiles WHERE baseline_swot IS NULL'))==0
    finally:
        nested.rollback()
