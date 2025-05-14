"""Client Tests."""
from flask import url_for
from ..views import web


def test_home_page(testing_db):
    """Test home page."""
    response = testing_db.get(url_for('web.home_page'))
    assert 'Welcome' in response.get_data(as_text=True)
