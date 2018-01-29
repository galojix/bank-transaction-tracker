"""Module that handles the database."""
import dateutil.parser
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from .password import hash_password, password_verified

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Class that instantiates a user table."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(250), nullable=False)
    businesses = db.relationship(
        "Business", order_by="Business.busname", back_populates="user",
        cascade="all, delete-orphan")
    categories = db.relationship(
        "Category", order_by="Category.catname", back_populates="user",
        cascade="all, delete-orphan")
    accounts = db.relationship(
        "Account", order_by="Account.accname", back_populates="user",
        cascade="all, delete-orphan")
    transactions = db.relationship(
        "Transaction", order_by="Transaction.date", back_populates="user",
        cascade="all, delete-orphan")

    @property
    def password(self):
        """Getter that raises an exception if attempt to read password."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Setter that hashes then sets password."""
        self.password_hash = hash_password(password)

    def verify_password(self, password):
        """Instance method that verifies password is correct."""
        return password_verified(password, self.password_hash)

    def add_business(self, busname):
        """Instance method that adds a business category."""
        self.businesses.append(Business(busname=busname))

    def add_category(self, catname, cattype):
        """Instance method that adds a user category."""
        self.categories.append(Category(catname=catname, cattype=cattype))

    def add_account(self, accname, balance):
        """Instance method that a user account."""
        self.accounts.append(Account(accname=accname, balance=balance))

    def add_transaction(self, amount, date, busname, catname, accname):
        """Instance method that adds a user transaction."""
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


class Business(db.Model):
    """Class that instantiates a businesses table."""

    __tablename__ = 'businesses'
    busno = db.Column(db.Integer, autoincrement=True, primary_key=True)
    busname = db.Column(db.String(250), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="businesses")
    transactions = db.relationship(
        "Transaction", order_by="Transaction.date", back_populates="business")


class Category(db.Model):
    """Class that instantiates a categories table."""

    __tablename__ = 'categories'
    catno = db.Column(db.Integer, primary_key=True)
    catname = db.Column(db.String(250), nullable=False)
    cattype = db.Column(db.String(250), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(User, back_populates="categories")
    transactions = db.relationship(
        "Transaction", order_by="Transaction.date", back_populates="category")


class Account(db.Model):
    """Class that instantiates an accounts table."""

    __tablename__ = 'accounts'
    accno = db.Column(db.Integer, primary_key=True)
    accname = db.Column(db.String(250), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(User, back_populates="accounts")
    transactions = db.relationship(
        "Transaction", order_by="Transaction.date", back_populates="account")


class Transaction(db.Model):
    """Class that instantiates a transactions table."""

    __tablename__ = 'transactions'
    transno = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    busno = db.Column(
        db.Integer, db.ForeignKey('businesses.busno'), nullable=False)
    business = db.relationship(Business, back_populates="transactions")
    catno = db.Column(
        db.Integer, db.ForeignKey('categories.catno'), nullable=False)
    category = db.relationship(Category, back_populates="transactions")
    accno = db.Column(
        db.Integer, db.ForeignKey('accounts.accno'), nullable=False)
    account = db.relationship(Account, back_populates="transactions")
    id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(User, back_populates="transactions")


def empty_database():
    """Delete existing database tables and recreate empty ones."""
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create new tables
