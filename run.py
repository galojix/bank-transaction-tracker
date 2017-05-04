"""Module that runs application in development mode."""
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
import os
from pft import create_app
from pft.database import db, User, Business, Category, Account, Transaction


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """Create a shell context so that can use REPL."""
    return dict(app=app, db=db, User=User, Business=Business,
                Category=Category, Account=Account, Transaction=Transaction)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
