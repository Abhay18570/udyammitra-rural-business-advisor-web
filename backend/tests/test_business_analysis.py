import uuid
from copy import deepcopy
import pytest
from sqlalchemy import select, func, update, text
from app.models.business import BusinessProfile
from app.models.business_analysis import BusinessAnalysis
from app.models.financial import FinancialAnalysis
from app.models.market_poi import MarketPOI
from app.models.profile import EntrepreneurProfile
from app.engines.nearby_market_engine import fingerprint
from app.schemas.business_analysis import BusinessAnalysisContext
from app.engines.competitor_analysis_engine import analyze_competition
from tests.test_nearby_market import osm, setup_user, expire
from tests.test_financial import analyze
from tests.test_feasibility import auth, register


def prepare(client, db, slug='tailoring-alteration', margin='14000.00'):
    token=setup_user(client)
    business=db.scalar(select(BusinessProfile).where(BusinessProfile.slug==slug))
    assert client.put('/api/v1/profile', headers=auth(token), json={'proposed_business_id':str(business.id),'own_capital':margin,'onboarding_step':3}).status_code==200
    financial=analyze(client,token,margin,slug).json()
    return token,financial['id']


def run(client,token,financial_id,**extra):
    return client.post('/api/v1/business-analysis',headers=auth(token),json={'financial_analysis_id':financial_id,'radius_km':5,**extra})


def test_full_analysis_snapshot_reproducibility(client,db_session,osm):
    token,financial_id=prepare(client,db_session)
    response=run(client,token,financial_id)
    assert response.status_code==201,response.text
    body=response.json()
    assert body['competition']['direct_count']==1
    assert body['pricing']['items']==[]
    assert body['financial_context']['scheme']['scheme_financing_gap']=='1000.00'
    ids={e['id'] for e in body['evidence']}
    for finding in body['local_threats']+[i for items in body['swot'].values() for i in items]:
        assert set(finding['evidence_ids'])<=ids
    row=db_session.get(BusinessAnalysis,uuid.UUID(body['id']))
    assert fingerprint(row.evidence_snapshot)==row.context_hash
    context=BusinessAnalysisContext.model_validate(row.evidence_snapshot)
    assert analyze_competition(context)==body['competition']
    db_session.execute(update(MarketPOI).values(name='Changed cache record'))
    db_session.flush()
    saved=client.get('/api/v1/business-analysis/'+body['id'],headers=auth(token))
    assert saved.json()==body
    # New analyses do not mutate previous snapshots.
    assert run(client,token,financial_id).status_code==201
    assert client.get('/api/v1/business-analysis/'+body['id'],headers=auth(token)).json()==body


def test_auth_and_owner_isolation(client,db_session,osm):
    token,fid=prepare(client,db_session)
    assert client.post('/api/v1/business-analysis',json={'financial_analysis_id':fid,'radius_km':5}).status_code==401
    saved=run(client,token,fid).json()
    other=register(client,'analysis-other')
    assert run(client,other,fid).status_code==404
    assert run(client,token,str(uuid.uuid4())).status_code==404
    assert client.get('/api/v1/business-analysis/'+saved['id'],headers=auth(other)).status_code==404
    assert client.get('/api/v1/business-analysis/'+saved['id']).status_code==401


@pytest.mark.parametrize('extra',[{'radius_km':v} for v in [0,11,-1,1.5,5.0,True,'5']]+[{k:'fake'} for k in ['competitor_count','coordinates','swot','threats','prices','financial_values','osm_tags','market_analysis_id']])
def test_strict_request(client,db_session,osm,extra):
    token,fid=prepare(client,db_session)
    assert run(client,token,fid,**extra).status_code==422
    assert osm['requests']==[]


@pytest.mark.parametrize('change,expected', [('missing_business','PROPOSED_BUSINESS_REQUIRED'),('business','PROPOSED_BUSINESS_MISMATCH'),('location','PROFILE_LOCATION_REQUIRED'),('catalog','CATALOG_COSTS_CHANGED'),('financial','inconsistent_financial_snapshot'),('version','unsupported_financial_version')])
def test_source_validation(client,db_session,osm,change,expected):
    token,fid=prepare(client,db_session)
    row=db_session.get(FinancialAnalysis,uuid.UUID(fid))
    profile=db_session.scalar(select(EntrepreneurProfile).where(EntrepreneurProfile.user_id==row.user_id))
    if change=='missing_business': profile.proposed_business_id=None
    elif change=='business': profile.proposed_business_id=db_session.scalar(select(BusinessProfile.id).where(BusinessProfile.slug=='kirana-general-store'))
    elif change=='location': profile.village=None
    elif change=='catalog': db_session.get(BusinessProfile,row.business_profile_id).estimated_setup_cost_min+=1
    elif change=='financial': row.indicative_loan_amount+=1
    elif change=='version': row.analysis_version='future-v2'
    db_session.flush()
    response=run(client,token,fid)
    assert response.status_code==409,response.text
    assert response.json()['detail']['code']==expected
    assert db_session.scalar(select(func.count()).select_from(BusinessAnalysis))==0
    assert osm['requests']==[]


def test_changed_budget_is_explicit_and_optional_evidence(client,db_session,osm):
    token,fid=prepare(client,db_session)
    client.put('/api/v1/profile',headers=auth(token),json={'own_capital':'15000','onboarding_step':3})
    body=run(client,token,fid).json()
    assert body['financial_context']['budget']['consistency_status']=='DIFFERENT'
    assert 'budget-different' in {i['rule_id'] for i in body['swot']['weaknesses']}
    client.put('/api/v1/profile',headers=auth(token),json={'own_capital':None,'onboarding_step':3})
    body=run(client,token,fid).json()
    assert body['financial_context']['budget']['consistency_status']=='NOT_RECORDED'


@pytest.mark.parametrize('failure', ['geocoder','ambiguous','overpass'])
def test_provider_failures_do_not_save(client,db_session,osm,failure):
    from tests.test_geocoding import candidate
    token,fid=prepare(client,db_session)
    if failure=='geocoder': osm['geocoder_fail']=True
    elif failure=='ambiguous': osm['geocoding']=[candidate(),candidate(lat='19.26')]
    else: osm['fail']=True
    response=run(client,token,fid)
    assert response.status_code==(409 if failure=='ambiguous' else 503),response.text
    assert db_session.scalar(select(func.count()).select_from(BusinessAnalysis))==0


def test_stale_fallback_withholds_label(client,db_session,osm):
    token,fid=prepare(client,db_session)
    initial=run(client,token,fid).json()
    expire(db_session)
    osm['fail']=True
    response=run(client,token,fid)
    assert response.status_code==201,response.text
    body=response.json()
    assert body['competition']['classification']=='STALE_EVIDENCE'
    assert body['market_context']['source']['cache_status']=='STALE_CACHE'
    assert body['market_context']['competitors']==initial['market_context']['competitors']


def test_change_during_provider_call_rejected(client,db_session,osm,monkeypatch):
    from app.services.business_analysis_service import NearbyMarketService
    token,fid=prepare(client,db_session)
    original=NearbyMarketService.analyze
    def changed(self,user,payload):
        result=original(self,user,payload)
        db_session.execute(update(EntrepreneurProfile).values(own_capital=999))
        db_session.flush()
        return result
    monkeypatch.setattr(NearbyMarketService,'analyze',changed)
    response=run(client,token,fid)
    assert response.status_code==409 and response.json()['detail']['code']=='ANALYSIS_CONTEXT_CHANGED'
    assert db_session.scalar(select(func.count()).select_from(BusinessAnalysis))==0


def test_database_snapshot_immutable(client,db_session,osm):
    from sqlalchemy.exc import DBAPIError
    token,fid=prepare(client,db_session)
    body=run(client,token,fid).json()
    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(text('UPDATE business_analyses SET selected_radius=3 WHERE id=:id'),{'id':body['id']})
    assert client.get('/api/v1/business-analysis/'+body['id'],headers=auth(token)).json()==body


def test_empty_market_does_not_claim_unmet_demand(client,db_session,osm):
    token,fid=prepare(client,db_session)
    osm['elements']=[]
    body=run(client,token,fid).json()
    assert body['competition']['classification']=='NO_MAPPED_DIRECT_EVIDENCE'
    assert body['competition']['direct_count']==0
    assert not any(i['source_type'] == 'MARKET' or 'market' in i['evidence_ids'] for i in body['swot']['opportunities'])
    assert not any('competition' in item['rule_id'] for item in body['swot']['strengths'])


def test_inactive_business_and_incomplete_market(client,db_session,osm,monkeypatch):
    from app.services.business_analysis_service import NearbyMarketService
    token,fid=prepare(client,db_session)
    original=NearbyMarketService.analyze
    def incomplete(self,user,payload):
        value=original(self,user,payload)
        value.quality.complete_query=False
        return value
    monkeypatch.setattr(NearbyMarketService,'analyze',incomplete)
    response=run(client,token,fid)
    assert response.status_code==409 and response.json()['detail']['code']=='MARKET_COVERAGE_INCOMPLETE'
    assert db_session.scalar(select(func.count()).select_from(BusinessAnalysis))==0
    row=db_session.get(FinancialAnalysis,uuid.UUID(fid))
    db_session.get(BusinessProfile,row.business_profile_id).is_active=False
    db_session.flush()
    assert run(client,token,fid).status_code==404


def test_catalog_knowledge_hash_changes_without_rewriting_previous(client,db_session,osm):
    token,fid=prepare(client,db_session)
    before=run(client,token,fid).json()
    row=db_session.get(FinancialAnalysis,uuid.UUID(fid))
    business=db_session.get(BusinessProfile,row.business_profile_id)
    business.major_risks=business.major_risks+['Explicit test catalog risk']
    db_session.flush()
    after=run(client,token,fid).json()
    assert before['business']['catalog_hash']!=after['business']['catalog_hash']
    assert client.get('/api/v1/business-analysis/'+before['id'],headers=auth(token)).json()==before


def test_existing_business_metrics_not_inferred_from_broad_category(client,db_session,osm):
    from tests.test_profile import complete_payload
    token,fid=prepare(client,db_session)
    payload=complete_payload(existing=True)
    payload.update(state='Maharashtra',district='Thane',taluka='Bhiwandi',village='Mankoli')
    assert client.put('/api/v1/profile',headers=auth(token),json=payload).status_code==200
    body=run(client,token,fid).json()
    assert body['profile_context']['existing_business_observations'] is None
