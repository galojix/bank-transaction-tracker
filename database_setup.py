import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DATE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    username = Column(String(250), primary_key=True)
    password = Column(String(250), nullable=False)
    salt = Column(String(250), nullable=False)


class Business(Base):
    __tablename__ = 'business'
    busno = Column(Integer, primary_key=True)
    busname = Column(String(250), nullable=False)
    username = Column(String(250), ForeignKey('user.username'))
    user = relationship(User, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE 
  

class Category(Base):
    __tablename__ = 'category'
    catno = Column(Integer, primary_key=True)
    catname = Column(String(250), nullable=False)
    cattype = Column(String(250), nullable=False)
    username = Column(String(250), ForeignKey('user.username'), nullable=False)    
    user = relationship(User, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    


class Account(Base):
    __tablename__ = 'account'
    accno = Column(Integer, primary_key=True)
    accname = Column(String(250), nullable=False)
    balance = Column(Integer, nullable=False)


class Transaction(Base):
    __tablename__ = 'transaction'
    transno = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    date = Column(DATE, nullable=False)  
    busno = Column(Integer, ForeignKey('business.busno'), nullable=False)
    business = relationship(Business, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE
    catno = Column(Integer, ForeignKey('category.catno'), nullable=False, )
    category = relationship(Category, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    
    accno = Column(Integer, ForeignKey('account.accno'), nullable=False)
    account = relationship(Account, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    
    username = Column(String(250), ForeignKey('user.username'))        
    user = relationship(User, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    


class AccountUser(Base):
    __tablename__ = 'accountuser'
    username = Column(String(250), ForeignKey('user.username'), primary_key=True)
    user = relationship(User, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE    
    accNo = Column(Integer, ForeignKey('account.accno'), primary_key=True)
    account = relationship(Account, cascade="all, delete-orphan") # ON UPDATE CASCADE ON DELETE CASCADE


engine = create_engine('sqlite:///bam.db')


Base.metadata.create_all(engine)


