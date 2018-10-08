"""User Model Tests."""
import pytest
import time
from .. import create_app, db
from ..database import User


@pytest.fixture(autouse=True)
def initialise_testing_db():
    """Create database before testing, delete after."""
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()
    app_context.pop()


def test_password_setter():
    """Test password is hashed and set."""
    u = User(password='cat')
    assert u.password_hash is not None


def test_no_password_getter():
    """Test can not get password."""
    u = User(password='cat')
    with pytest.raises(AttributeError):
        u.password


def test_password_verification():
    """Test password verification."""
    u = User(password='cat')
    assert u.verify_password('cat')
    assert not u.verify_password('dog')


def test_password_salts_are_random():
    """Test password salts are random."""
    u = User(password='cat')
    u2 = User(password='cat')
    assert u.password_hash != u2.password_hash


def test_valid_confirmation_token():
    """Test valid confirmation token."""
    u = User(email='test1', password='cat')
    db.session.add(u)
    db.session.commit()
    token = u.generate_confirmation_token()
    assert u.confirm(token)


def test_invalid_confirmation_token():
    """Test invalid confirmation token."""
    u1 = User(email='test1', password='cat')
    u2 = User(email='test2', password='dog')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    token = u1.generate_confirmation_token()
    assert not u2.confirm(token)


def test_expired_confirmation_token():
    """Test expired confirmation token."""
    u = User(email='test1', password='cat')
    db.session.add(u)
    db.session.commit()
    token = u.generate_confirmation_token(1)
    time.sleep(2)
    assert not u.confirm(token)
