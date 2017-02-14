from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Business, Category, Account, Transaction, AccountUser 

engine = create_engine('sqlite:///bam.db')
Base.metadata.bind = engine
Base.metadata.drop_all(engine) # Drop all existing tables
Base.metadata.create_all(engine) # Create new tables 

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create users
user1 = User(username="demo", password="demo", salt="tba")
session.add(user1)
session.commit()

user2 = User(username="normal", password="normal", salt="tba")
session.add(user2)
session.commit()

# Create businesses
business1 = Business(busname="Acme", username="demo")
session.add(business1)
session.commit()

business2 = Business(busname="Caltex", username="demo")
session.add(business2)
session.commit()
