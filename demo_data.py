from database_setup import Base, User, Business, Category, Account, Transaction, AccountUser, session, empty_database 
from lib_common import hash_password, password_verified

# Start with an empty database
empty_database()

# Create users
user1 = User(username="demo", password=hash_password("demo"))
session.add(user1)
session.commit()

user2 = User(username="normal", password=hash_password("normal"))
session.add(user2)
session.commit()

# Create businesses
business1 = Business(busname="Acme", username="demo")
session.add(business1)
session.commit()

business2 = Business(busname="Caltex", username="demo")
session.add(business2)
session.commit()

