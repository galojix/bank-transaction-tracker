"""Module that runs application in development mode."""
import os
import click
from pft import create_app
from pft.database import db, User, Category, Account, Transaction
from pft.demo_db import create_db
import unittest
from pft.classification import test_classification


app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    """Create a shell context so that can use REPL."""
    return dict(app=app, db=db, User=User, Category=Category, Account=Account,
                Transaction=Transaction)


@app.cli.command()
def test():
    """Run the unit tests."""
    tests = unittest.TestLoader().discover('pft.tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def demo():
    """Create a demo database."""
    print("Creating a new demo database...")
    create_db()
    print("Done.")


@app.cli.command()
@click.argument('name')
def classify(name):
    """Test transaction categorization for user name."""
    test_classification(name)
