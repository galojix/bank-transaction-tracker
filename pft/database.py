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
        Business(busname=busname, user=self)

    def add_category(self, catname, cattype):
        """Instance method that adds a user category."""
        Category(catname=catname, cattype=cattype, user=self)

    def add_account(self, accname, balance):
        """Instance method that a user account."""
        Account(accname=accname, balance=balance, user=self)

    def add_transaction(self, amount, date, busname, catname, accname):
        """Instance method that adds a user transaction."""
        date = dateutil.parser.parse(date)
        business = [b for b in self.businesses if b.busname == busname][0]
        category = [c for c in self.categories if c.catname == catname][0]
        account = [a for a in self.accounts if a.accname == accname][0]
        Transaction(
            amount=amount, date=date, user=self, business=business,
            category=category, account=account)

    def __repr__(self):
        """Represent user as id and email address."""
        return '<User:{num},{name}>'.format(num=self.id, name=self.email)


class Business(db.Model):
    """Class that instantiates a businesses table."""

    __tablename__ = 'businesses'
    busno = db.Column(db.Integer, primary_key=True)
    busname = db.Column(db.String(250), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="businesses")
    transactions = db.relationship(
        "Transaction", order_by="Transaction.date", back_populates="business")

    def __repr__(self):
        """Represent business as business number and name."""
        return '<Bus:{num},{name}>'.format(num=self.busno, name=self.busname)


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

    def __repr__(self):
        """Represent category as category number and name."""
        return '<Cat:{num},{name}>'.format(num=self.catno, name=self.catname)


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

    def __repr__(self):
        """Represent account as account number and name."""
        return '<Acc:{num},{name}>'.format(num=self.accno, name=self.accname)


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

    def __repr__(self):
        """Represent transaction as transaction number and user."""
        return '<Trans:{num},{name}>'.format(
            num=self.transno, name=self.user.email)


def empty_database():
    """Delete existing database tables and recreate empty ones."""
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create new tables
