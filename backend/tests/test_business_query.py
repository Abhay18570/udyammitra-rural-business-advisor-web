import json
import time
import httpx
import pytest
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from app.business_query_rules import classify_query
from app.providers.google_places import GooglePlacesProvider, TEXT_FIELD_MASK, build_text_payload
from app.providers.errors import ProviderError
from app.providers.nearby import ProviderPolicy
from app.schemas.nearby_market import NearbyMarketRequest
from app.models.market_poi import MarketPOI
from app.models.market_cache import NearbyQueryCache
from app.repositories.nearby_market_repository import NearbyMarketRepository
from tests.test_google_places import settings, place
from tests.test_google_nearby import google
from tests.test_nearby_market import setup_user
from tests.test_feasibility import auth

@pytest.mark.parametrize('value', ['', ' ', 'a', 'x'*201])
def test_invalid_query(value):
    with pytest.raises(ValidationError): NearbyMarketRequest(business_query=value, radius_km=5)

def test_contract():
    assert NearbyMarketRequest(business_query='  Tea   Stall  ', radius_km=3).business_query == 'Tea Stall'
    assert NearbyMarketRequest(business_slug='tailoring-alteration', radius_km=5).business_query is None
    for radius in [0,11,1.5,True,'5']:
        with pytest.raises(ValidationError): NearbyMarketRequest(business_query='Bakery',radius_km=radius)

@pytest.mark.parametrize('radius', [1000,5000,10000])
def test_text_request_pagination(radius):
    requests=[]
    def handler(request):
        requests.append(request)
        return httpx.Response(200,json={'places':[place(str(len(requests)),'tea_house')],'nextPageToken':str(len(requests))})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        pois,bad=GooglePlacesProvider(settings(),client).fetch_text('  Tea   Stall ',19,73,time.monotonic()+10,radius)
    assert len(requests)==len(pois)==2 and bad==0
    first=requests[0]
    assert str(first.url)=='https://places.googleapis.com/v1/places:searchText'
    assert first.headers['X-Goog-Api-Key']=='mock-backend-key'
    assert first.headers['X-Goog-FieldMask']==TEXT_FIELD_MASK
    assert not any(s in TEXT_FIELD_MASK.lower() for s in ['rating','review','photo'])
    assert 'mock-backend-key' not in str(first.url)+first.content.decode()
    body=json.loads(first.content)
    assert body=={'textQuery':'Tea Stall','pageSize':20,'locationBias':{'circle':{'center':{'latitude':19,'longitude':73},'radius':radius}}}
    assert json.loads(requests[1].content)=={**body,'pageToken':'1'}
    assert pois[0]['provider']=='GOOGLE_PLACES'

@pytest.mark.parametrize('query,name,primary,expected',[
 ('Kirana Store','Hari OM','grocery_store','DIRECT_COMPETITOR'),
 ('Tea Stall','Example','cafe','RELATED_BUSINESS'),
 ('Mobile Repair Shop','Phone Planet','cell_phone_store','RELATED_BUSINESS'),
 ('Mobile Repair Shop','Raj phone repair','cell_phone_store','DIRECT_COMPETITOR'),
 ('Agricultural Equipment Rental','Equipment Sales','store','RELATED_BUSINESS'),
 ('Computer Repair Shop','Random','restaurant','GENERIC_POI'),
 ('Organic Tea Stall','Tea House','tea_house','RELATED_BUSINESS')])
def test_classification(query,name,primary,expected):
    match=classify_query(query,name,{'primary_type':primary})
    assert match['classification']==expected
    assert 'confidence' not in match

@pytest.mark.parametrize('status',[400,403,500,503,429])
def test_errors(status):
    with httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(status,text='private diagnostics'))) as client:
        with pytest.raises(ProviderError) as exc: GooglePlacesProvider(settings(),client).fetch_text('Bakery',19,73,time.monotonic()+10,5000)
    assert exc.value.status==(429 if status==429 else 503)
    assert 'private' not in str(exc.value)

def test_timeout():
    def fail(request): raise httpx.ReadTimeout('private')
    with httpx.Client(transport=httpx.MockTransport(fail)) as client:
        with pytest.raises(ProviderError) as exc: GooglePlacesProvider(settings(),client).fetch_text('Bakery',19,73,time.monotonic()+10,5000)
    assert exc.value.code=='PROVIDER_TIMEOUT'

@pytest.mark.parametrize('raw',[[],{'places':None},{'places':[{'id':'bad'}]},{'places':[],'nextPageToken':42}])
def test_malformed(raw):
    with httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json=raw))) as client:
        with pytest.raises(ProviderError): GooglePlacesProvider(settings(),client).fetch_text('Bakery',19,73,time.monotonic()+10,5000)

def test_identity_validation():
    policy=ProviderPolicy(settings(nearby_market_provider='google'))
    loc={'latitude':19,'longitude':73,'location_fingerprint':'x'}
    key=policy.text_request_key('Bakery',loc,5000)
    assert key!=policy.text_request_key('Tea Stall',loc,5000)
    assert key!=policy.text_request_key('Bakery',loc,3000)
    assert key!=ProviderPolicy(settings(nearby_market_provider='google',google_places_text_max_pages=1)).text_request_key('Bakery',loc,5000)
    assert key!=ProviderPolicy(settings()).text_request_key('Bakery',loc,5000)
    for lat,lon in [(91,73),(19,181),(float('nan'),73)]:
        with pytest.raises(ValueError): build_text_payload('Bakery',lat,lon,5000,20)
    with pytest.raises(ValidationError): settings(google_places_text_search_url='https://example.org')

def search(client,token,query='Tea Stall',radius=3):
    return client.post('/api/v1/market/nearby',headers=auth(token),json={'business_query':query,'radius_km':radius})

def test_live_transient_postgis(client,db_session,google):
    token=setup_user(client)
    google['places']=[place('direct','tea_house'),place('related','cafe'),place('generic','hardware_store'),place('outside','tea_house',location={'latitude':20,'longitude':73})]
    response=search(client,token,'  Tea   Stall ')
    assert response.status_code==200,response.text
    assert response.headers['cache-control']=='no-store'
    body=response.json()
    assert body['business_query']=='Tea Stall' and body['matched_catalog_business_slug'] is None
    assert body['summary']['direct_competitors']==body['summary']['related_businesses']==1
    assert len(body['generic_pois'])==1
    assert all(p['distance_meters']<=3000 for p in body['competitors']+body['related_businesses']+body['generic_pois'])
    assert 'GOOGLE_RANKED_SUBSET' in [w['code'] for w in body['quality']['warnings']]
    assert db_session.scalar(select(func.count()).select_from(MarketPOI).where(MarketPOI.provider=='GOOGLE_PLACES'))==0
    assert db_session.scalar(select(func.count()).select_from(NearbyQueryCache).where(NearbyQueryCache.provider=='GOOGLE_PLACES'))==0
    assert search(client,token).json()['source']['mode']=='LIVE'
    google['status']=503
    assert search(client,token).status_code==503
    assert not any('overpass' in r.url.host for r in google['requests'])

def test_empty_spatial_failure(client,google,monkeypatch):
    token=setup_user(client)
    google['places']=[]
    assert search(client,token).json()['summary']['nearest_direct_competitor'] is None
    def fail(*args): raise OperationalError('hidden',{},Exception('hidden'))
    monkeypatch.setattr(NearbyMarketRepository,'spatial_candidates',fail)
    result=search(client,token)
    assert result.status_code==503 and result.json()['detail']['code']=='SPATIAL_QUERY_FAILED'
    assert 'hidden' not in result.text

def test_overpass_limitation(client,google):
    token=setup_user(client)
    google['settings'].nearby_market_provider='overpass'
    result=search(client,token,'Computer Repair Shop')
    assert result.status_code==422 and result.json()['detail']['code']=='OVERPASS_CATALOG_REQUIRED'

def test_storage_guard():
    with pytest.raises(ValueError): NearbyMarketRepository(None).save_query('k',{},'s','v',[],60,provider='GOOGLE_PLACES')

@pytest.mark.parametrize('radius',[1,5,10])
def test_transient_boundary(db_session,radius):
    from sqlalchemy import cast
    from geoalchemy2 import Geometry
    from app.utils.spatial import geography_point
    pois=[]
    for i,meters in enumerate([radius*1000-0.01,radius*1000+0.01,radius*1000]):
        point=cast(func.ST_Project(geography_point(19,73),meters,0.0),Geometry('POINT',srid=4326))
        lat,lon=db_session.execute(select(func.ST_Y(point),func.ST_X(point))).one()
        pois.append({'external_id':str(i),'latitude':lat,'longitude':lon})
    result=NearbyMarketRepository(db_session).spatial_candidates(pois,{'latitude':19,'longitude':73},radius*1000)
    assert [p['external_id'] for p in result]==['0','2']
    assert result[1]['distance_meters']==radius*1000
    assert result[0]['distance_meters']<=radius*1000


def test_exact_catalog_match_and_profile_unchanged(client,db_session,google):
    from app.models.business import BusinessProfile
    token=setup_user(client)
    before=client.get('/api/v1/profile',headers=auth(token)).json()
    business=db_session.scalar(select(BusinessProfile).where(BusinessProfile.slug=='tailoring-alteration'))
    body=search(client,token,business.name).json()
    assert body['matched_catalog_business_slug']==business.slug
    assert body['business']['id']==str(business.id)
    assert search(client,token,'Agricultural Equipment Rental').status_code==200
    assert client.get('/api/v1/profile',headers=auth(token)).json()==before
    google['settings'].nearby_market_provider='overpass'
    assert search(client,token,business.name).status_code==200


def test_repeated_page_token_and_dedup():
    requests=[]
    def handler(r):
        requests.append(r)
        return httpx.Response(200,json={'places':[place()],'nextPageToken':'same'})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ProviderError): GooglePlacesProvider(settings(),client).fetch_text('Bakery',19,73,time.monotonic()+10,5000)
    assert len(requests)==2
