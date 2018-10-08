"""Basic Unit Tests."""
import pytest
from flask import current_app
from .. import create_app
from ..database import db


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


def test_app_exists():
    """Test app exists."""
    assert current_app is not None


def test_app_is_testing():
    """Test app is testing."""
    assert current_app.config['TESTING']
