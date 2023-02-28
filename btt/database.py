"""Module that handles the database."""
import dateutil.parser
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from itsdangerous import BadSignature, Serializer, TimedSerializer
from .password import hash_password, password_verified

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Class that instantiates a users table."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(250), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    memberships = db.relationship(
        "MemberShip",
        order_by="MemberShip.id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def password(self):
        """Getter that raises an exception if attempt to read password."""
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        """Setter that hashes then sets password."""
        self.password_hash = hash_password(password)

    def verify_password(self, password):
        """Instance method that verifies password is correct."""
        return password_verified(password, self.password_hash)

    def generate_confirmation_token(self):
        """Generate confirmation token."""
        s = TimedSerializer(current_app.secret_key, "confirmation")
        return s.dumps({"confirm": self.id})

    def confirm(self, token, max_age=3600):
        """Confirm token."""
        s = TimedSerializer(current_app.secret_key, "confirmation")
        try:
            data = s.loads(token, max_age=max_age)
        except BadSignature:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email):
        """Generate email change token."""
        s = TimedSerializer(current_app.secret_key, "confirmation")
        return s.dumps({"change_email": self.id, "new_email": new_email})

    def change_email(self, token, max_age=3600):
        """Change email address."""
        s = TimedSerializer(current_app.secret_key, "confirmation")
        try:
            data = s.loads(token, max_age=max_age)
        except BadSignature:
            return False
        if data.get("change_email") != self.id:
            return False
        new_email = data.get("new_email")
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_reset_token(self):
        """Generate password reset token."""
        s = TimedSerializer(current_app.secret_key, "confirmation")
        return s.dumps({"reset": self.id})

    @staticmethod
    def reset_password(token, new_password):
        """Reset password."""
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except BadSignature:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def group(self):
        """Get active group for current user."""
        for membership in self.memberships:
            if membership.active:
                group = membership.group
        return group

    def __repr__(self):
        """Represent user as id and email address."""
        return "<User:{num},{name}>".format(num=self.id, name=self.email)


class Group(db.Model):
    """Class that instantiates a groups table."""

    __tablename__ = "groups"
    group_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    categories = db.relationship(
        "Category",
        order_by="Category.catname",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    accounts = db.relationship(
        "Account",
        order_by="Account.accname",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    transactions = db.relationship(
        "Transaction",
        order_by="Transaction.date",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    memberships = db.relationship(
        "MemberShip",
        order_by="MemberShip.group_id",
        back_populates="group",
        cascade="all, delete-orphan",
    )

    def add_category(self, catname, cattype):
        """Instance method that adds a user category."""
        Category(catname=catname, cattype=cattype, group=self)

    def add_categories_accounts(self):
        """Add standard categories and accounts."""
        categories = (
            ("Bank Fees", "Expense"),
            ("Education, Training, Sport", "Expense"),
            ("Entertainment", "Expense"),
            ("Food and Groceries", "Expense"),
            ("Gifts and Donations", "Expense"),
            ("Health Care", "Expense"),
            ("Holidays", "Expense"),
            ("Housing", "Expense"),
            ("Interest and Investment Income", "Income"),
            ("Investment Expenses", "Expense"),
            ("Kids", "Expense"),
            ("Pets", "Expense"),
            ("Refunds", "Income"),
            ("Salary", "Income"),
            ("Shopping", "Expense"),
            ("Transfer In", "Transfer In"),
            ("Transfer Out", "Transfer Out"),
            ("Transport", "Expense"),
            ("Unspecified Expense", "Expense"),
            ("Unspecified Income", "Income"),
            ("Utilities", "Expense"),
            ("Work Expenses", "Expense"),
        )
        for catname, cattype in categories:
            self.add_category(catname=catname, cattype=cattype)

        accounts = (
            "Bank A Term Deposit",
            "Bank A Transaction",
            "Bank B Credit Card",
            "Bank C Credit Card",
            "Bank D Term Deposit",
            "Bank E Term Deposit",
            "Bank F Transaction",
            "Bank G Transaction",
            "Unknown",
        )
        for accname in accounts:
            self.add_account(accname=accname)

    def add_account(self, accname):
        """Instance method that adds a user account."""
        Account(accname=accname, group=self)

    def add_transaction(
        self,
        amount,
        date,
        description,
        catname,
        accname,
        dayfirst=True,
        yearfirst=False,
    ):
        """Instance method that adds a user transaction."""
        date = dateutil.parser.parse(
            date, dayfirst=dayfirst, yearfirst=yearfirst
        )
        category = [c for c in self.categories if c.catname == catname][0]
        account = [a for a in self.accounts if a.accname == accname][0]
        Transaction(
            amount=amount,
            date=date,
            group=self,
            category=category,
            description=description,
            account=account,
        )

    def __repr__(self):
        """Represent groups as group_id and name."""
        return "<Group:{num},{name}>".format(num=self.group_id, name=self.name)


class MemberShip(db.Model):
    """Class that instantiates a memberships table."""

    __tablename__ = "memberships"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    group_id = db.Column(
        db.Integer, db.ForeignKey("groups.group_id"), primary_key=True
    )
    active = db.Column(db.Boolean, default=False)
    user = db.relationship(User, back_populates="memberships")
    group = db.relationship(Group, back_populates="memberships")

    def __repr__(self):
        """Represent membership as user_id and group_id."""
        return "<Mem:{num1},{num2}>".format(num1=self.id, num2=self.group_id)


class Category(db.Model):
    """Class that instantiates a categories table."""

    __tablename__ = "categories"
    catno = db.Column(db.Integer, primary_key=True)
    catname = db.Column(db.String(250), nullable=False, index=True)
    cattype = db.Column(db.String(250), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    group = db.relationship(Group, back_populates="categories")
    transactions = db.relationship(
        "Transaction", order_by="Transaction.date", back_populates="category"
    )

    def __repr__(self):
        """Represent category as category number and name."""
        return "<Cat:{num},{name}>".format(num=self.catno, name=self.catname)


class Account(db.Model):
    """Class that instantiates an accounts table."""

    __tablename__ = "accounts"
    accno = db.Column(db.Integer, primary_key=True)
    accname = db.Column(db.String(250), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    group = db.relationship(Group, back_populates="accounts")
    transactions = db.relationship(
        "Transaction", order_by="Transaction.date", back_populates="account"
    )

    def __repr__(self):
        """Represent account as account number and name."""
        return "<Acc:{num},{name}>".format(num=self.accno, name=self.accname)


class Transaction(db.Model):
    """Class that instantiates a transactions table."""

    __tablename__ = "transactions"
    transno = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, index=True)
    description = db.Column(db.String(250))
    catno = db.Column(
        db.Integer, db.ForeignKey("categories.catno"), nullable=False
    )
    category = db.relationship(Category, back_populates="transactions")
    accno = db.Column(
        db.Integer, db.ForeignKey("accounts.accno"), nullable=False
    )
    account = db.relationship(Account, back_populates="transactions")
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    group = db.relationship(Group, back_populates="transactions")

    def __repr__(self):
        """Represent transaction as transaction number and group name."""
        return "<Trans:{num},{name}>".format(
            num=self.transno, name=self.group.name
        )


def empty_database():
    """Delete existing database tables and recreate empty ones."""
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create new tables


def create_db():
    """Create new database and demo user."""
    empty_database()
    user = User(email="demo@demo.demo", password="demo", confirmed=True)
    group = Group(name="Test")
    membership = MemberShip(user=user, group=group, active=True)
    group.add_categories_accounts()
    db.session.add(user)
    db.session.add(group)
    db.session.add(membership)
    db.session.commit()
