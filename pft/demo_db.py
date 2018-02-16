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
    user = User(
        email="demo@demo.demo", name="Demo", password="demo", confirmed=True)
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
                  ("Interest", "Income"),
                  ("Unspecified Expense", "Expense"),
                  ("Unspecified Income", "Income"),
                  ("Transfer In", "Transfer In"),
                  ("Transfer Out", "Transfer Out"))
    for catname, cattype in categories:
        user.add_category(catname=catname, cattype=cattype)

    # Create user's accounts
    accounts = (("NAB", 50000), ("ANZ", 20000), ("Unknown", 0))
    for accname, balance in accounts:
        user.add_account(accname=accname, balance=balance)

    # Create user's transactions
    transactions = (
        (7007, "2016-10-01T08:05", "Bupa", "Insurance", "NAB"),
        (6007, "2016-10-02T08:06", "ABC Corp", "Entertainment", "NAB"),
        (8008, "2016-10-03T08:07", "Bupa", "Insurance", "NAB"),
        (700, "2016-10-04T08:15", "Coles", "Food", "ANZ"),
        (75000, "2016-10-05T08:05", "Coles", "Food", "ANZ"),
        (85000, "2016-10-06T08:25", "Wonka", "Salary", "ANZ"),
        (7007, "2016-10-01T08:05", "Bupa", "Insurance", "NAB"),
        (6007, "2016-10-02T08:06", "ABC Corp", "Entertainment", "NAB"),
        (8008, "2016-10-03T08:07", "Bupa", "Insurance", "NAB"),
        (700, "2016-10-04T08:15", "Coles", "Food", "ANZ"),
        (75000, "2016-10-05T08:05", "Coles", "Food", "ANZ"),
        (85000, "2016-10-06T08:25", "Wonka", "Salary", "ANZ"),
        (7007, "2016-10-07T08:05", "Bupa", "Insurance", "NAB"),
        (6007, "2016-10-08T08:06", "ABC Corp", "Entertainment", "NAB"),
        (8008, "2016-10-09T08:07", "Bupa", "Insurance", "NAB"),
        (700, "2016-10-10T08:15", "Coles", "Food", "ANZ"),
        (75000, "2016-11-11T08:05", "Coles", "Food", "ANZ"),
        (85000, "2016-10-12T08:25", "Acme", "Interest", "ANZ"),
        (7007, "2016-10-13T08:05", "Bupa", "Insurance", "NAB"),
        (6007, "2016-10-14T08:06", "ABC Corp", "Entertainment", "NAB"),
        (8008, "2016-10-15T08:07", "Bupa", "Insurance", "NAB"),
        (700, "2016-10-16T08:15", "Coles", "Food", "ANZ"),
        (75000, "2016-10-17T08:05", "Coles", "Food", "ANZ"),
        (85000, "2016-10-18T08:25", "Wonka", "Salary", "ANZ"),
        (7007, "2016-10-19T08:05", "Bupa", "Insurance", "NAB"),
        (10000, "2016-10-18T08:35", "Unknown", "Transfer Out", "ANZ"),
        (10000, "2016-10-19T08:45", "Unknown", "Transfer In", "NAB"),
        (6007, "2016-10-20T08:06", "ABC Corp", "Entertainment", "NAB"),
        (8008, "2016-10-21T08:07", "Bupa", "Insurance", "NAB"),
        (700, "2016-10-22T08:15", "Coles", "Food", "ANZ"),
        (75000, "2016-10-23T08:05", "Coles", "Food", "ANZ"),
        (85000, "2016-10-24T08:25", "Wonka", "Salary", "ANZ"))
    for amount, date, busname, catname, accname in transactions:
        user.add_transaction(
            amount=amount, date=date, busname=busname, catname=catname,
            accname=accname)

    db.session.add(user)
    db.session.commit()

    # Create user
    user = User(
        email="normal@demo.demo", name="Normal", password="normal",
        confirmed=True)

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
    transactions = (
        (8007, "2016-10-01T08:05", "Bupa", "Insurance", "NAB"),
        (9007, "2016-10-01T08:06", "ABC Corp", "Entertainment", "NAB"))
    for amount, date, busname, catname, accname in transactions:
        user.add_transaction(
            amount=amount, date=date, busname=busname, catname=catname,
            accname=accname)

    db.session.add(user)
    db.session.commit()
