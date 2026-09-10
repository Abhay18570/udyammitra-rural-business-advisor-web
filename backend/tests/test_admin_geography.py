from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import pytest
from sqlalchemy import select

from app.data.business_seed import seed_businesses
from app.models.business import BusinessProfile
from app.models.profile import EntrepreneurProfile
from app.models.user import UserRole
from tests.test_admin import empty_users, make_user, headers

BASE = '/api/v1/admin'


@pytest.fixture
def geography(empty_users):
    db = empty_users
    admin = make_user(db, UserRole.ADMIN, state='Excluded', district='Excluded')
    make_user(db, UserRole.SUPER_ADMIN, state='Excluded', district='Excluded')
    users = [
        make_user(db, state=' Test State ', district=' Common ', village='Needle Village', has_existing_business=False, onboarding_completed=True),
        make_user(db, state='TEST  STATE', district='COMMON', has_existing_business=True),
        make_user(db, state='test state', district='Other', has_existing_business=False),
        make_user(db, state='Test State', district='  ', has_existing_business=None),
        make_user(db, state='Second State', district='Common', has_existing_business=True),
        make_user(db, state=' \t ', district='Unknown', has_existing_business=None),
        make_user(db),
    ]
    for index, user in enumerate(users):
        user.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=index)
    db.flush()
    return db, admin, users


@pytest.mark.parametrize('path', ['/analytics/states','/analytics/states/test%20state/districts','/entrepreneurs'])
@pytest.mark.parametrize('role,code', [(None,401),(UserRole.USER,403),(UserRole.ADMIN,200),(UserRole.SUPER_ADMIN,200)])
def test_authorization(client, geography, path, role, code):
    db, _, _ = geography
    auth = headers(make_user(db, role)) if role else {}
    assert client.get(BASE + path, headers=auth).status_code == code


def test_state_counts(client, geography):
    _, admin, _ = geography
    data = client.get(BASE+'/analytics/states', headers=headers(admin)).json()
    assert data['total_entrepreneurs'] == 6
    assert data['located_entrepreneurs'] == 5
    assert data['missing_state_count'] == 1
    assert data['states_count'] == 2 and data['districts_count'] == 3
    assert [(r['state_key'], r['entrepreneur_count'], r['percentage']) for r in data['states']] == [('test state',4,'80.00'),('second state',1,'20.00')]
    row = data['states'][0]
    assert (row['new_enterprises'],row['existing_enterprises'],row['districts_count']) == (2,1,2)
    assert 'email' not in str(data) and 'password' not in str(data)


def test_district_scope_and_missing(client, geography):
    _, admin, _ = geography
    data = client.get(BASE+'/analytics/states/'+quote(' TEST  STATE ',safe='')+'/districts', headers=headers(admin)).json()
    assert data['total_entrepreneurs'] == 4 and data['missing_district_count'] == 1
    assert data['districts_count'] == 2
    assert [(r['district_key'],r['entrepreneur_count'],r['percentage']) for r in data['districts']] == [('common',2,'66.67'),('other',1,'33.33')]
    assert (data['new_enterprises'],data['existing_enterprises']) == (2,1)
    assert data['districts'][0]['new_enterprises'] == 1
    assert data['districts'][0]['existing_enterprises'] == 1


@pytest.mark.parametrize('state', ['nonexistent', "' OR 1=1 --", ' '])
def test_unknown_state(client, geography, state):
    _, admin, _ = geography
    assert client.get(BASE+'/analytics/states/'+quote(state,safe='')+'/districts',headers=headers(admin)).status_code == 404


def test_empty(client, empty_users):
    admin = make_user(empty_users, UserRole.ADMIN)
    data = client.get(BASE+'/analytics/states',headers=headers(admin)).json()
    assert data == dict(total_entrepreneurs=0,located_entrepreneurs=0,missing_state_count=0,states_count=0,districts_count=0,states=[])


def test_all_locations_missing(client, empty_users):
    admin = make_user(empty_users, UserRole.ADMIN)
    make_user(empty_users, state=None)
    data = client.get(BASE+'/analytics/states',headers=headers(admin)).json()
    assert data['total_entrepreneurs'] == data['missing_state_count'] == 1 and data['states'] == []


def test_state_without_district(client, empty_users):
    admin = make_user(empty_users, UserRole.ADMIN)
    make_user(empty_users, state='State / Special & Name', district=None)
    response = client.get(BASE+'/analytics/states/'+quote('State / Special & Name',safe='')+'/districts',headers=headers(admin))
    assert response.status_code == 200
    assert response.json()['districts'] == [] and response.json()['missing_district_count'] == 1


def test_list_pagination_and_privacy(client, geography):
    _, admin, users = geography
    auth = headers(admin)
    one = client.get(BASE+'/entrepreneurs',params={'page_size':2},headers=auth)
    data = one.json()
    assert one.headers['cache-control'] == 'no-store'
    assert (data['total'],data['page'],data['page_size'],data['total_pages']) == (7,1,2,4)
    assert [r['email'] for r in data['items']] == [users[6].email,users[5].email]
    assert data['items'][0]['profile_status'] == 'pending'
    assert set(data['items'][0]) == {'full_name','email','mobile_number','preferred_language','created_at','state','district','taluka','village','proposed_business','enterprise_status','profile_status'}
    last = client.get(BASE+'/entrepreneurs',params={'page_size':2,'page':4},headers=auth).json()
    assert len(last['items']) == 1
    assert client.get(BASE+'/entrepreneurs',params={'page':99},headers=auth).json()['items'] == []


@pytest.mark.parametrize('params,total', [
    ({'state':' TEST  STATE '},4),({'district':' common '},3),({'state':'test state','district':'common'},2),
    ({'enterprise_status':'new'},2),({'enterprise_status':'existing'},2),({'enterprise_status':'unspecified'},3),
    ({'state':'absent'},0),({'search':'Needle Village'},1),({'search':'common'},3),({'search':'TEST STATE'},3),
    ({'search':'%'},0),({'search':"' OR 1=1 --"},0),
])
def test_list_filters(client, geography, params, total):
    _, admin, _ = geography
    data = client.get(BASE+'/entrepreneurs',params=params,headers=headers(admin)).json()
    assert data['total'] == total


@pytest.mark.parametrize('field', ['email','mobile_number'])
def test_search_account(client, geography, field):
    _, admin, users = geography
    data = client.get(BASE+'/entrepreneurs',params={'search':getattr(users[0],field)},headers=headers(admin)).json()
    assert data['total'] == 1 and data['items'][0]['email'] == users[0].email


@pytest.mark.parametrize('sort', ['created_asc','created_desc'])
def test_sort(client, geography, sort):
    _, admin, users = geography
    data = client.get(BASE+'/entrepreneurs',params={'sort':sort},headers=headers(admin)).json()
    expected = users if sort == 'created_asc' else list(reversed(users))
    assert [r['email'] for r in data['items']] == [u.email for u in expected]


@pytest.mark.parametrize('params', [{'page_size':101},{'page_size':0},{'page':0},{'sort':'email desc'},{'enterprise_status':'bad'},{'search':'x'*161}])
def test_invalid_filters(client, geography, params):
    _, admin, _ = geography
    assert client.get(BASE+'/entrepreneurs',params=params,headers=headers(admin)).status_code == 422


def test_business_join_and_completion(client, geography):
    db, admin, users = geography
    seed_businesses(db)
    business = db.scalar(select(BusinessProfile).limit(1))
    p = db.scalar(select(EntrepreneurProfile).where(EntrepreneurProfile.user_id == users[0].id))
    p.proposed_business_id = business.id
    db.flush()
    data = client.get(BASE+'/entrepreneurs',params={'business_slug':business.slug},headers=headers(admin)).json()
    assert data['total'] == 1
    assert data['items'][0]['proposed_business'] == business.name
    assert data['items'][0]['profile_status'] == 'complete'
