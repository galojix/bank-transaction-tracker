"""Module that runs application in development mode."""
from flask_script import Manager, Shell
import os
from pft import create_app
from pft.database import db, User, Category, Account, Transaction
from pft.demo_db import create_db
import unittest


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    """Create a shell context so that can use REPL."""
    return dict(app=app, db=db, User=User, Category=Category, Account=Account,
                Transaction=Transaction)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test():
    """Run the unit tests."""
    tests = unittest.TestLoader().discover('pft.tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def demo():
    """Create a demo database."""
    print("Creating a new demo database...")
    create_db()
    print("Done.")


if __name__ == '__main__':
    manager.run()
