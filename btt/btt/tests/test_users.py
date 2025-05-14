"""User Model Tests."""
import pytest
import time
from .. import db
from ..database import User


def test_password_setter(testing_db):
    """Test password is hashed and set."""
    u = User(password='cat')
    assert u.password_hash is not None


def test_no_password_getter(testing_db):
    """Test can not get password."""
    u = User(password='cat')
    with pytest.raises(AttributeError):
        u.password


def test_password_verification(testing_db):
    """Test password verification."""
    u = User(password='cat')
    assert u.verify_password('cat')
    assert not u.verify_password('dog')


def test_password_salts_are_random(testing_db):
    """Test password salts are random."""
    u = User(password='cat')
    u2 = User(password='cat')
    assert u.password_hash != u2.password_hash


def test_valid_confirmation_token(testing_db):
    """Test valid confirmation token."""
    u = User(email='test1', password='cat')
    db.session.add(u)
    db.session.commit()
    token = u.generate_confirmation_token()
    assert u.confirm(token)


def test_invalid_confirmation_token(testing_db):
    """Test invalid confirmation token."""
    u1 = User(email='test1', password='cat')
    u2 = User(email='test2', password='dog')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    token = u1.generate_confirmation_token()
    assert not u2.confirm(token)


def test_expired_confirmation_token(testing_db):
    """Test expired confirmation token."""
    u = User(email='test1', password='cat')
    db.session.add(u)
    db.session.commit()
    token = u.generate_confirmation_token(1)
    time.sleep(2)
    assert not u.confirm(token)
