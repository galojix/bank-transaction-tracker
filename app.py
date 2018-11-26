"""Module that runs application in development mode."""
import os
import click
from btt import create_app
from btt.database import (
    db, User, Category, Account, Transaction, Group, MemberShip, create_db)
import unittest
from btt.classification import classification_score


app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    """Create a shell context so that can use REPL."""
    return dict(app=app, db=db, User=User, Category=Category, Account=Account,
                Transaction=Transaction, Group=Group, MemberShip=MemberShip)


@app.cli.command()
def test():
    """Run the unit tests."""
    tests = unittest.TestLoader().discover('btt.tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def newdb():
    """Create a new empty database."""
    print('This operation will overwrite any existing databases.')
    ans = input('Are you sure you want to create a new empty database y/n ? ')
    if ans == 'y':
        print('Creating new empty database...')
        create_db()
        print("Done.")
        print("Do not forget to change the demo account password!!!")
    else:
        print('No action taken.')


@app.cli.command()
@click.argument('group_id')
def classify(group_id):
    """Test transaction categorization for email."""
    score, data_size, num_features = classification_score(group_id)
    print('Score: ', score)
    print('Data Size: ', data_size)
    print('Number of Features: ', num_features)
