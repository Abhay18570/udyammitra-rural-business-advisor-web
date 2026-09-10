from unittest.mock import Mock
import pytest
from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from app.core.config import Settings
from app.core.security import verify_password
from app.models.user import User, UserRole
from scripts.bootstrap_admin import BootstrapError, bootstrap_admin

PASSWORD = 'BootstrapTestOnly123'

def config(**changes):
    return Settings(_env_file=None, bootstrap_admin_email='BOOTSTRAP-TEST@example.com', bootstrap_admin_password=SecretStr(PASSWORD), bootstrap_admin_mobile='+91 8765432198').model_copy(update=changes)

def account(db):
    return db.scalar(select(User).where(User.email == 'bootstrap-test@example.com'))

@pytest.mark.parametrize('field', ['bootstrap_admin_email', 'bootstrap_admin_password', 'bootstrap_admin_mobile'])
def test_missing(db_session, field):
    with pytest.raises(BootstrapError, match='configuration is incomplete'):
        bootstrap_admin(db_session, config(**{field: None}))
    assert account(db_session) is None

def test_creation_idempotence(db_session, capsys):
    before = db_session.scalar(select(func.count()).select_from(User))
    print(bootstrap_admin(db_session, config()))
    user = account(db_session)
    assert user.role == UserRole.ADMIN and user.is_active
    assert user.mobile_number == '8765432198'
    assert user.preferred_language.value == 'en' and user.created_at
    assert user.password_hash != PASSWORD and user.password_hash.startswith('$argon2id$')
    assert verify_password(PASSWORD, user.password_hash)
    original = user.password_hash
    print(bootstrap_admin(db_session, config(bootstrap_admin_password=SecretStr('DifferentTest123'))))
    db_session.refresh(user)
    assert user.password_hash == original
    assert db_session.scalar(select(func.count()).select_from(User)) == before + 1
    output = capsys.readouterr().out
    assert PASSWORD not in output and original not in output
    assert 'Admin account already exists.' in output

@pytest.mark.parametrize('role', [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.USER])
def test_existing_roles(db_session, role):
    bootstrap_admin(db_session, config())
    user = account(db_session)
    user.role = role
    user.is_active = False
    db_session.commit()
    original = user.password_hash
    if role == UserRole.USER:
        with pytest.raises(BootstrapError, match='non-admin role'):
            bootstrap_admin(db_session, config())
    else:
        assert bootstrap_admin(db_session, config()) == 'Admin account already exists.'
    db_session.refresh(user)
    assert user.role == role and not user.is_active and user.password_hash == original

def test_mobile_conflict(db_session):
    bootstrap_admin(db_session, config())
    with pytest.raises(BootstrapError, match='Mobile number belongs'):
        bootstrap_admin(db_session, config(bootstrap_admin_email='other-bootstrap@example.com'))
    assert db_session.scalar(select(User).where(User.email == 'other-bootstrap@example.com')) is None

@pytest.mark.parametrize('changes', [{'bootstrap_admin_email': 'invalid'}, {'bootstrap_admin_mobile': '123'}, {'bootstrap_admin_password': SecretStr('invalid')}])
def test_invalid(db_session, changes):
    with pytest.raises(BootstrapError) as exc:
        bootstrap_admin(db_session, config(**changes))
    assert str(exc.value) == 'Bootstrap admin configuration is invalid.'

def test_race_rollback():
    db = Mock()
    db.scalar.return_value = None
    db.commit.side_effect = IntegrityError('secret SQL', {}, Exception(PASSWORD))
    with pytest.raises(BootstrapError) as exc:
        bootstrap_admin(db, config())
    db.rollback.assert_called_once()
    assert PASSWORD not in str(exc.value)

def test_public_registration(client):
    response = client.post('/api/v1/auth/register', json={'full_name': 'Registration Test', 'email': 'bootstrap-public@example.com', 'mobile_number': '8765432197', 'preferred_language': 'en', 'password': PASSWORD, 'role': 'ADMIN'})
    assert response.status_code == 201
    assert response.json()['user']['role'] == 'USER'
