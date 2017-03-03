import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dateutil.parser

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    username = Column(String(250), primary_key=True)
    password = Column(String(250), nullable=False)
    businesses = relationship("Business", order_by="Business.busname", back_populates="user", cascade="all, delete, delete-orphan") 
    categories = relationship("Category", order_by="Category.catname", back_populates="user", cascade="all, delete, delete-orphan")
    accounts = relationship("Account", order_by="Account.accname", back_populates="user", cascade="all, delete, delete-orphan")
    transactions = relationship("Transaction", order_by="Transaction.date", back_populates="user", cascade="all, delete, delete-orphan")
    
    def add_business(self, busname):
        self.businesses.append(Business(busname=busname))
   
    def add_category(self, catname, cattype):
        self.categories.append(Category(catname=catname, cattype=cattype))             

    def add_account(self, accname, balance):
        self.accounts.append(Account(accname=accname, balance=balance))
        
    def add_transaction(self, amount, date, busname, catname, accname):
        date = dateutil.parser.parse(date)
        transaction = Transaction(amount=amount, date=date)        
        for business in self.businesses:
            if business.busname == busname:
                business.transactions.append(transaction)
        for category in self.categories:
            if category.catname == catname:
                category.transactions.append(transaction)
        for account in self.accounts:
            if account.accname == accname:
                account.transactions.append(transaction)
        self.transactions.append(transaction)
    
class Business(Base):
    __tablename__ = 'business'
    busno = Column(Integer, autoincrement=True, primary_key=True)
    busname = Column(String(250), nullable=False)
    username = Column(String(250), ForeignKey('user.username'))
    user = relationship("User", back_populates="businesses")
    transactions = relationship("Transaction", order_by="Transaction.date", back_populates="business", cascade="all, delete-orphan")  
  

class Category(Base):
    __tablename__ = 'category'
    catno = Column(Integer, primary_key=True)
    catname = Column(String(250), nullable=False)
    cattype = Column(String(250), nullable=False)
    username = Column(String(250), ForeignKey('user.username'), nullable=False)    
    user = relationship(User, back_populates="categories")    
    transactions = relationship("Transaction", order_by="Transaction.date", back_populates="category", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = 'account'
    accno = Column(Integer, primary_key=True)
    accname = Column(String(250), nullable=False)
    balance = Column(Integer, nullable=False)
    username = Column(String(250), ForeignKey('user.username'), nullable=False)    
    user = relationship(User, back_populates="accounts")     
    transactions = relationship("Transaction", order_by="Transaction.date", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = 'tranzaction'
    transno = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)  
    busno = Column(Integer, ForeignKey('business.busno'), nullable=False)
    business = relationship(Business, back_populates="transactions") 
    catno = Column(Integer, ForeignKey('category.catno'), nullable=False, )
    category = relationship(Category, back_populates="transactions")     
    accno = Column(Integer, ForeignKey('account.accno'), nullable=False)
    account = relationship(Account, back_populates="transactions")     
    username = Column(String(250), ForeignKey('user.username'))        
    user = relationship(User, back_populates="transactions")     

engine = create_engine('sqlite:///bam.db', echo=True)

Base.metadata.create_all(engine) 

DBSession = sessionmaker(bind=engine)
sqlsession = DBSession()

def empty_database():
    Base.metadata.drop_all(engine) # Drop all existing tables
    Base.metadata.create_all(engine) # Create new tables 

