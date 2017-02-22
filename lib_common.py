from passlib.hash import pbkdf2_sha256
from database_setup import User, Business, Category, Account, Transaction, session
import dateutil.parser

def hash_password(password):
    # generate new salt, and hash a password    
    return pbkdf2_sha256.hash(password)

    
def password_verified(password, hash):
    return pbkdf2_sha256.verify(password, hash)
    
    
def add_user(name, passwd):
    user = User(username=name, password=hash_password(passwd))
    session.add(user)
    session.commit()


def add_business(bus_name, user):
    business = Business(busname=bus_name, username=user)
    session.add(business)
    session.commit()
        

def add_category(cat_name, cat_type, user):
    category = Category(catname=cat_name, cattype=cat_type, username=user)
    session.add(category)
    session.commit()


def add_account(acc_name, balance, user):
    account = Account(accname=acc_name, balance=balance, username=user)
    session.add(account)
    session.commit()
    
def add_transaction(amount, date, busno, catno, accno, user):
    date = dateutil.parser.parse(date)
    transaction = Transaction(amount=amount, date=date, busno=busno, catno=catno, accno=accno, username=user)
    session.add(transaction)
    session.commit()


