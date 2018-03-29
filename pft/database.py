"""Module that handles the database."""
import dateutil.parser
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
from .password import hash_password, password_verified

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Class that instantiates a user table."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(250), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
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

    def add_category(self, catname, cattype):
        """Instance method that adds a user category."""
        Category(catname=catname, cattype=cattype, user=self)

    def add_account(self, accname):
        """Instance method that a user account."""
        Account(accname=accname, user=self)

    def add_transaction(self, amount, date, description, catname, accname,
                        dayfirst=True, yearfirst=False):
        """Instance method that adds a user transaction."""
        date = dateutil.parser.parse(
            date, dayfirst=dayfirst, yearfirst=yearfirst)
        category = [c for c in self.categories if c.catname == catname][0]
        account = [a for a in self.accounts if a.accname == accname][0]
        Transaction(
            amount=amount, date=date, user=self, category=category,
            description=description, account=account)

    def generate_confirmation_token(self, expiration=3600):
        """Generate confirmation token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        """Confirm token."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except BadSignature:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        """Generate email change token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        """Change email address."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except BadSignature:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        """Generate password reset token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        """Reset password."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except BadSignature:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def __repr__(self):
        """Represent user as id and email address."""
        return '<User:{num},{name}>'.format(num=self.id, name=self.email)


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
    category_patterns = db.relationship(
        "CategoryPattern", order_by="CategoryPattern.pattern",
        back_populates="category")

    def __repr__(self):
        """Represent category as category number and name."""
        return '<Cat:{num},{name}>'.format(num=self.catno, name=self.catname)


class CategoryPattern(db.Model):
    """Class that instantiates a category pattern table."""

    __tablename__ = 'categorypatterns'
    pattern_no = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(250), nullable=False)
    catno = db.Column(db.Integer, db.ForeignKey('categories.catno'))
    category = db.relationship(Category, back_populates="category_patterns")

    def __repr__(self):
        """Represent category pattern as pattern number and pattern."""
        return '<CatPattern:{num},{name}>'.format(
            num=self.pattern_no, name=self.pattern)


class Account(db.Model):
    """Class that instantiates an accounts table."""

    __tablename__ = 'accounts'
    accno = db.Column(db.Integer, primary_key=True)
    accname = db.Column(db.String(250), nullable=False)
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
    description = db.Column(db.String(250))
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
