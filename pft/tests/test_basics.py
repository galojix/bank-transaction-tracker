"""Basic Unit Tests."""
import unittest
from flask import current_app
from .. import create_app
from ..database import db


class BasicsTestCase(unittest.TestCase):
    """Basic Test Case."""

    def setUp(self):
        """Set up tests."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        """Test app exists."""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """Test app is testing."""
        self.assertTrue(current_app.config['TESTING'])
