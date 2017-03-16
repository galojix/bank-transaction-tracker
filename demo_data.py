from web import User, db, empty_database
from lib_common import hash_password

# Start with an empty database
empty_database()

# Create user
user = User(username="demo", password=hash_password("demo"))

# Create user's businesses
businesses = ("Acme", "Wonka", "ABC Corp", "Bupa", "Coles", "Galojix", "Lowes",
              "Caltex", "Unknown")
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
transactions = ((7007, "2016-10-01T08:05", "Bupa", "Insurance", "NAB"),
                (6007, "2016-10-01T08:06", "ABC Corp", "Entertainment", "NAB"))
for amount, date, busname, catname, accname in transactions:
    user.add_transaction(amount=amount, date=date, busname=busname,
                         catname=catname, accname=accname)

db.session.add(user)
db.session.commit()

# Create user
user = User(username="normal", password=hash_password("normal"))

# Create user's businesses
businesses = ("Acme", "Wonka", "ABC Corp", "Bupa", "Coles", "Galojix", "Lowes",
              "Caltex", "Unknown")
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
                (9007, "2016-10-01T08:06", "ABC Corp", "Entertainment", "NAB"))
for amount, date, busname, catname, accname in transactions:
    user.add_transaction(amount=amount, date=date, busname=busname,
                         catname=catname, accname=accname)

db.session.add(user)
db.session.commit()
