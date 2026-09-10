import uuid

import pytest
from sqlalchemy import delete

from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.models.profile import EntrepreneurProfile


@pytest.fixture
def empty_users(db_session):
    # Test transaction is rolled back by the shared PostgreSQL fixture.
    db_session.execute(delete(User))
    db_session.flush()
    return db_session


def make_user(db, role=UserRole.USER, **profile):
    user = User(full_name='Overview Test', email=f'{uuid.uuid4()}@example.com',
                mobile_number=str(uuid.uuid4().int)[:10], password_hash='unused-test-hash', role=role, is_active=True)
    db.add(user)
    db.flush()
    if profile:
        db.add(EntrepreneurProfile(user_id=user.id, **profile))
        db.flush()
    return user


def headers(user):
    return {'Authorization': f'Bearer {create_access_token(user)}'}


def test_unauthenticated(client):
    assert client.get('/api/v1/admin/overview').status_code == 401


@pytest.mark.parametrize('role,status', [(UserRole.USER,403),(UserRole.ADMIN,200),(UserRole.SUPER_ADMIN,200)])
def test_roles(client, db_session, role, status):
    user = make_user(db_session, role)
    response = client.get('/api/v1/admin/overview', headers=headers(user))
    assert response.status_code == status


def test_real_aggregates(client, empty_users):
    db = empty_users
    admin = make_user(db, UserRole.ADMIN, state='Excluded', district='Excluded', has_existing_business=True)
    make_user(db, UserRole.SUPER_ADMIN, state='Other excluded', district='Other', has_existing_business=False)
    make_user(db)
    make_user(db, state=' Maharashtra ', district=' Pune ', has_existing_business=False)
    make_user(db, state='MAHARASHTRA', district='pune', has_existing_business=True)
    make_user(db, state='Karnataka', district='Pune', has_existing_business=False)
    make_user(db, state=' \t ', district='Unknown', has_existing_business=None)
    make_user(db, state='Maharashtra', district=None, has_existing_business=None)
    make_user(db, state=None, district=None, has_existing_business=None)
    response = client.get('/api/v1/admin/overview', headers=headers(admin))
    assert response.status_code == 200
    assert response.json() == dict(total_registered_users=7, total_entrepreneurs=6, profiles_pending=1,
                                  new_enterprises=2, existing_enterprises=1, states_count=2, districts_count=2)
    assert all(type(value) is int for value in response.json().values())


def test_empty_aggregates(client, empty_users):
    admin = make_user(empty_users, UserRole.ADMIN)
    data = client.get('/api/v1/admin/overview', headers=headers(admin)).json()
    assert len(data) == 7 and set(data.values()) == {0}


def test_current_database_role_authoritative(client, db_session):
    user = make_user(db_session, UserRole.ADMIN)
    token = headers(user)
    user.role = UserRole.USER
    db_session.flush()
    assert client.get('/api/v1/admin/overview', headers=token).status_code == 403


def test_inactive_admin_denied(client, db_session):
    user = make_user(db_session, UserRole.ADMIN)
    token = headers(user)
    user.is_active = False
    db_session.flush()
    assert client.get('/api/v1/admin/overview', headers=token).status_code == 401
