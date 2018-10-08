"""Fixture for pytest."""
import pytest
from .. import create_app, db


@pytest.fixture()
def testing_db():
    """Create database before testing, delete after."""
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    client = app.test_client(use_cookies=True)
    yield client
    db.session.remove()
    db.drop_all()
    app_context.pop()
