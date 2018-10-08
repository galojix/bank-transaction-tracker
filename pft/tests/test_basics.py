"""Basic Unit Tests."""
from flask import current_app


def test_app_exists(testing_db):
    """Test app exists."""
    assert current_app is not None


def test_app_is_testing(testing_db):
    """Test app is testing."""
    assert current_app.config['TESTING']
