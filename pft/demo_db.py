"""Module that creates new database for demo purposes."""
import os
from . import create_app
from .database import db, empty_database, User


def create_db():
    """Create demo database."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    db.init_app(app)

    # Tell SQLAlchemy what the current app is
    # app.app_context().push()
    # Start with an empty database
    empty_database()
    # Create user
    user = User(email="demo@demo.demo", password="demo")
    # Create user's businesses
    businesses = ("Acme", "Wonka", "ABC Corp", "Bupa", "Coles", "Galojix",
                  "Lowes", "Caltex", "Unknown")
    for business in businesses:
        user.add_business(busname=business)

    # Create user's categories
    categories = (("Food", "Expense"),
                  ("Entertainment", "Expense"),
                  ("Insurance", "Expense"),
                  ("Salary", "Income"),
                  ("Unspecified Expense", "Expense"),
                  ("Unspecified Income", "Income"))
    for catname, cattype in categories:
        user.add_category(catname=catname, cattype=cattype)

    # Create user's accounts
    accounts = (("NAB", 50000), ("ANZ", 20000), ("Unknown", 0))
    for accname, balance in accounts:
        user.add_account(accname=accname, balance=balance)

    # Create user's transactions
    transactions = ((7007, "2016-10-01T08:05", "Bupa", "Insurance", "NAB"),
                    (6007, "2016-10-02T08:06", "ABC Corp", "Entertainment",
                     "NAB"),
                    (8008, "2016-10-03T08:07", "Bupa", "Insurance", "NAB"),
                    (700, "2016-10-04T08:15", "Coles", "Food", "ANZ"),
                    (75000, "2016-10-05T08:05", "Coles", "Food", "ANZ"),
                    (85000, "2016-10-06T08:25", "Wonka", "Salary", "ANZ"))
    for amount, date, busname, catname, accname in transactions:
        user.add_transaction(amount=amount, date=date, busname=busname,
                             catname=catname, accname=accname)

    db.session.add(user)
    db.session.commit()

    # Create user
    user = User(email="normal@demo.demo", password="normal")

    # Create user's businesses
    businesses = ("Acme", "Wonka", "ABC Corp", "Bupa", "Coles", "Galojix",
                  "Lowes", "Caltex", "Unknown")
    for business in businesses:
        user.add_business(busname=business)

    # Create user's categories
    categories = (("Food", "Expense"),
                  ("Entertainment", "Expense"),
                  ("Insurance", "Expense"),
                  ("Unspecified Expense", "Expense"),
                  ("Unspecified Income", "Income"))
    for catname, cattype in categories:
        user.add_category(catname=catname, cattype=cattype)

    # Create user's accounts
    accounts = (("NAB", 50000), ("ANZ", 20000), ("Unknown", 0))
    for accname, balance in accounts:
        user.add_account(accname=accname, balance=balance)

    # Create user's transactions
    transactions = ((8007, "2016-10-01T08:05", "Bupa", "Insurance", "NAB"),
                    (9007, "2016-10-01T08:06", "ABC Corp", "Entertainment",
                     "NAB"))
    for amount, date, busname, catname, accname in transactions:
        user.add_transaction(amount=amount, date=date, busname=busname,
                             catname=catname, accname=accname)

    db.session.add(user)
    db.session.commit()
