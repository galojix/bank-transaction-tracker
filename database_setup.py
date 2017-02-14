import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DATE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    userName = Column(String(250), primary_key=True)
    password = Column(String(250), nullable=False)
    salt = Column(String(250), nullable=False)


class Businesses(Base):
    __tablename__ = 'businesses'
    busNo = Column(Integer, primary_key=True)
    busName = Column(String(250), nullable=False)
    userName = Column(String(250), ForeignKey('users.userName'))
    users = relationship(Users, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE 
  

class Categories(Base):
    __tablename__ = 'categories'
    catNo = Column(Integer, primary_key=True)
    catName = Column(String(250), nullable=False)
    catType = Column(String(250), nullable=False)
    userName = Column(String(250), ForeignKey('users.userName'), nullable=False)    
    users = relationship(Users, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    


class Accounts(Base):
    __tablename__ = 'accounts'
    accNo = Column(Integer, primary_key=True)
    accName = Column(String(250), nullable=False)
    balance = Column(Integer, nullable=False)


class Transactions(Base):
    __tablename__ = 'transactions'
    transNo = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    date = Column(DATE, nullable=False)  
    busNo = Column(Integer, ForeignKey('businesses.busNo'), nullable=False)
    businesses = relationship(Businesses, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE
    catNo = Column(Integer, ForeignKey('categories.catNo'), nullable=False, )
    categories = relationship(Categories, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    
    accNo = Column(Integer, ForeignKey('accounts.accNo'), nullable=False)
    accounts = relationship(Accounts, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    
    userName = Column(String(250), ForeignKey('users.userName'))        
    users = relationship(Users, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    


class AccountsUsers(Base):
    __tablename__ = 'accountsusers'

    userName = Column(String(250), ForeignKey('users.userName'), primary_key=True)
    users = relationship(Users, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    
    accNo = Column(Integer, ForeignKey('accounts.accNo'), primary_key=True)
    accounts = relationship(Accounts, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE


engine = create_engine('sqlite:///bam.db')


Base.metadata.create_all(engine)



