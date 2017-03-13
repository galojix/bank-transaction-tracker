from flask import Flask, render_template, url_for, request, redirect, session, abort, flash
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from lib_common import password_verified
import dateutil.parser
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'pft.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(250), primary_key=True)
    password = db.Column(db.String(250), nullable=False)
    businesses = db.relationship("Business", order_by="Business.busname", back_populates="user", cascade="all, delete, delete-orphan") 
    categories = db.relationship("Category", order_by="Category.catname", back_populates="user", cascade="all, delete, delete-orphan")
    accounts = db.relationship("Account", order_by="Account.accname", back_populates="user", cascade="all, delete, delete-orphan")
    transactions = db.relationship("Transaction", order_by="Transaction.date", back_populates="user", cascade="all, delete, delete-orphan")
    
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
    transactions = db.relationship("Transaction", order_by="Transaction.date", back_populates="business", cascade="all, delete-orphan")  
  

class Category(db.Model):
    __tablename__ = 'categories'
    catno = db.Column(db.Integer, primary_key=True)
    catname = db.Column(db.String(250), nullable=False)
    cattype = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250), db.ForeignKey('users.username'), nullable=False)    
    user = db.relationship(User, back_populates="categories")    
    transactions = db.relationship("Transaction", order_by="Transaction.date", back_populates="category", cascade="all, delete-orphan")

class Account(db.Model):
    __tablename__ = 'accounts'
    accno = db.Column(db.Integer, primary_key=True)
    accname = db.Column(db.String(250), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(250), db.ForeignKey('users.username'), nullable=False)    
    user = db.relationship(User, back_populates="accounts")     
    transactions = db.relationship("Transaction", order_by="Transaction.date", back_populates="account", cascade="all, delete-orphan")

class Transaction(db.Model):
    __tablename__ = 'transactions'
    transno = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)  
    busno = db.Column(db.Integer, db.ForeignKey('businesses.busno'), nullable=False)
    business = db.relationship(Business, back_populates="transactions") 
    catno = db.Column(db.Integer, db.ForeignKey('categories.catno'), nullable=False, )
    category = db.relationship(Category, back_populates="transactions")     
    accno = db.Column(db.Integer, db.ForeignKey('accounts.accno'), nullable=False)
    account = db.relationship(Account, back_populates="transactions")     
    username = db.Column(db.String(250), db.ForeignKey('users.username'))        
    user = db.relationship(User, back_populates="transactions")     


def empty_database():
    db.drop_all() # Drop all existing tables
    db.create_all() # Create new tables 


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
    return render_template('home.html',transactions=transactions, menu="home")


@app.route('/login', methods=['POST'])
def login():
    try:    
        user = db.session.query(User).filter(User.username == request.form['username']).one()
    except sqlalchemy.orm.exc.NoResultFound:
        flash('*Invalid login, please try again.')
        return home_page()
    if password_verified(request.form['password'], user.password):
        session['logged_in'] = True
        session['user'] = user.username
    else:
        flash('*Invalid login, please try again.')
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
    return render_template('accounts.html',accounts=accounts, menu="accounts")


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
    return render_template('transactions.html',transactions=transactions, menu="transactions")


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
    
    if request.method == 'POST':

        if request.form['submit'] == 'Modify':

            if request.form['date']:
                transaction.date = dateutil.parser.parse(request.form['date'])

            if request.form['amount']:
                transaction.amount = request.form['amount']

            if request.form['busName']:
                for business in businesses:
                    if business.busname == request.form['busName'] and business.username == session['user']:
                        transaction.business = business

            if request.form['catName']:
                for category in categories:
                    if category.catname == request.form['catName'] and category.username == session['user']:
                        transaction.category = category

            if request.form['accName']:
                for account in accounts:
                    if account.accname == request.form['accName'] and account.username == session['user']:
                        transaction.account = account

            db.session.add(transaction)
            db.session.commit()

        if request.form['submit'] == 'Delete':
            db.session.delete(transaction)
            db.session.commit()

        if request.form['submit'] == 'Cancel':
            pass

        return redirect(url_for('transactions_page'))
    else:
        return render_template('modify_transaction.html',transaction=transaction,\
                                businesses=businesses, categories=categories,\
                                accounts=accounts, current_business=transaction.business.busname,\
                                current_category=transaction.category.catname,\
                                current_account = transaction.account.accname, menu="transactions")

@app.route('/businesses')
def businesses_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    businesses = db.session.query(Business).\
                    filter(Business.username == session['user']).\
                    all()
    return render_template('businesses.html',businesses=businesses, menu="businesses")


@app.route('/categories')
def categories_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    categories = db.session.query(Category).\
                    filter(Category.username == session['user']).\
                    all()
    return render_template('categories.html',categories=categories, menu="categories")


@app.route('/reports')
def reports_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('reports.html',menu="reports")

if __name__ == '__main__':
    app.secret_key = os.urandom(24) # Required for sessions, used for signing cookies
    app.debug = True
    app.run(port=5000)
