from flask import Flask, render_template, url_for, request, redirect, session,\
    flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from lib_common import password_verified
import dateutil.parser
import os
from sqlalchemy.orm.exc import NoResultFound

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'pft.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(250), primary_key=True)
    password = db.Column(db.String(250), nullable=False)
    businesses = db.relationship("Business", order_by="Business.busname",
                                 back_populates="user", cascade="all, delete,\
                                 delete-orphan")
    categories = db.relationship("Category", order_by="Category.catname",
                                 back_populates="user", cascade="all, delete,\
                                 delete-orphan")
    accounts = db.relationship("Account", order_by="Account.accname",
                               back_populates="user", cascade="all, delete,\
                               delete-orphan")
    transactions = db.relationship("Transaction", order_by="Transaction.date",
                                   back_populates="user", cascade="all, delete,\
                                   delete-orphan")

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


class Business(db.Model):
    __tablename__ = 'businesses'
    busno = db.Column(db.Integer, autoincrement=True, primary_key=True)
    busname = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250), db.ForeignKey('users.username'))
    user = db.relationship("User", back_populates="businesses")
    transactions = db.relationship("Transaction", order_by="Transaction.date",
                                   back_populates="business", cascade="all,\
                                   delete-orphan")


class Category(db.Model):
    __tablename__ = 'categories'
    catno = db.Column(db.Integer, primary_key=True)
    catname = db.Column(db.String(250), nullable=False)
    cattype = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250), db.ForeignKey('users.username'),
                         nullable=False)
    user = db.relationship(User, back_populates="categories")
    transactions = db.relationship("Transaction", order_by="Transaction.date",
                                   back_populates="category", cascade="all,\
                                   delete-orphan")


class Account(db.Model):
    __tablename__ = 'accounts'
    accno = db.Column(db.Integer, primary_key=True)
    accname = db.Column(db.String(250), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(250), db.ForeignKey('users.username'),
                         nullable=False)
    user = db.relationship(User, back_populates="accounts")
    transactions = db.relationship("Transaction", order_by="Transaction.date",
                                   back_populates="account", cascade="all,\
                                   delete-orphan")


class Transaction(db.Model):
    __tablename__ = 'transactions'
    transno = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    busno = db.Column(db.Integer, db.ForeignKey('businesses.busno'),
                      nullable=False)
    business = db.relationship(Business, back_populates="transactions")
    catno = db.Column(db.Integer, db.ForeignKey('categories.catno'),
                      nullable=False, )
    category = db.relationship(Category, back_populates="transactions")
    accno = db.Column(db.Integer, db.ForeignKey('accounts.accno'),
                      nullable=False)
    account = db.relationship(Account, back_populates="transactions")
    username = db.Column(db.String(250), db.ForeignKey('users.username'))
    user = db.relationship(User, back_populates="transactions")


def empty_database():
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create new tables


class ModifyTransactionForm(FlaskForm):
    date = DateTimeLocalField('Date:', format='%Y-%m-%dT%H:%M',
                              validators=[Required()])
    business_name = SelectField('Business Name:', validators=[Required()])
    category_name = SelectField('Category Name:', validators=[Required()])
    account_name = SelectField('Account Name:', validators=[Required()])
    amount = IntegerField('Amount:', validators=[Required()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


@app.route('/')
@app.route('/home')
def home_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    transactions = db.session.query(Transaction, Category, Business, Account).\
        filter(Transaction.username == session['user']).\
        filter(Transaction.catno == Category.catno).\
        filter(Transaction.busno == Business.busno).\
        filter(Transaction.accno == Account.accno).\
        all()
    return render_template('home.html', transactions=transactions, menu="home")


@app.route('/login', methods=['POST'])
def login():
    try:
        user = db.session.query(User).\
            filter(User.username == request.form['username']).one()
    except NoResultFound:
        flash('Invalid login, please try again.')
        return home_page()
    if password_verified(request.form['password'], user.password):
        session['logged_in'] = True
        session['user'] = user.username
    else:
        flash('Invalid login, please try again.')
    return home_page()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home_page()


@app.route('/accounts')
def accounts_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    accounts = db.session.query(Account).\
        filter(Account.username == session['user']).\
        all()
    return render_template('accounts.html', accounts=accounts, menu="accounts")


@app.route('/transactions')
def transactions_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    transactions = db.session.query(Transaction, Category, Business, Account).\
        filter(Transaction.username == session['user']).\
        filter(Transaction.catno == Category.catno).\
        filter(Transaction.busno == Business.busno).\
        filter(Transaction.accno == Account.accno).\
        all()
    return render_template('transactions.html', transactions=transactions,
                           menu="transactions")


@app.route('/transactions/modify/<int:transno>/', methods=['GET', 'POST'])
def modify_transaction(transno):
    if not session.get('logged_in'):
        return render_template('login.html')

    transaction = db.session.query(Transaction).\
        filter(Transaction.transno == transno).\
        one()
    businesses = db.session.query(Business).\
        filter(Business.username == session['user']).\
        all()
    categories = db.session.query(Category).\
        filter(Category.username == session['user']).\
        all()
    accounts = db.session.query(Account).\
        filter(Account.username == session['user']).\
        all()

    business_names = \
        [(business.busname, business.busname) for business in businesses]
    category_names = \
        [(category.catname, category.catname) for category in categories]
    account_names = \
        [(account.accname, account.accname) for account in accounts]

    form = ModifyTransactionForm()
    form.date.default = transaction.date
    form.business_name.choices = business_names
    form.business_name.default = transaction.business.busname
    form.category_name.choices = category_names
    form.category_name.default = transaction.category.catname
    form.account_name.choices = account_names
    form.account_name.default = transaction.account.accname
    form.amount.default = transaction.amount

    if form.validate_on_submit():
        if form.modify.data:
            transaction.date = form.date.data
            for business in businesses:
                if business.busname == form.business_name.data:
                    transaction.business = business
            for category in categories:
                if category.catname == form.category_name.data:
                    transaction.category = category
            for account in accounts:
                if account.accname == form.account_name.data:
                    transaction.account = account
            transaction.amount = form.amount.data
            db.session.add(transaction)
            db.session.commit()
        elif form.delete.data:
            db.session.delete(transaction)
            db.session.commit()
        elif form.cancel.data:
            pass
        return redirect(url_for('transactions_page'))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template('modify_transaction.html', form=form,
                           transno=transaction.transno, menu="transactions")


@app.route('/businesses')
def businesses_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    businesses = db.session.query(Business).\
        filter(Business.username == session['user']).\
        all()
    return render_template('businesses.html', businesses=businesses,
                           menu="businesses")


@app.route('/categories')
def categories_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    categories = db.session.query(Category).\
        filter(Category.username == session['user']).\
        all()
    return render_template('categories.html', categories=categories,
                           menu="categories")


@app.route('/reports')
def reports_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('reports.html', menu="reports")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.secret_key = os.urandom(24)  # Required for sessions
    app.debug = True
    app.run(port=5000)
