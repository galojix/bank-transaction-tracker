from flask import Flask, render_template, url_for, request, redirect, session, abort, flash
from database_setup import User, Transaction, Category, Business, Account, sqlsession
from lib_common import password_verified
import dateutil.parser
import os
import sqlalchemy.orm.exc


app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    transactions = sqlsession.query(Transaction, Category, Business, Account).\
                        filter(Transaction.username == session['user']).\
                        filter(Transaction.catno == Category.catno).\
                        filter(Transaction.busno == Business.busno).\
                        filter(Transaction.accno == Account.accno).\
                        all()
    return render_template('home.html',transactions=transactions, menu="home")


@app.route('/login', methods=['POST'])
def login():
    try:    
        user = sqlsession.query(User).filter(User.username == request.form['username']).one()
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
    accounts = sqlsession.query(Account).\
                    filter(Account.username == session['user']).\
                    all()
    return render_template('accounts.html',accounts=accounts, menu="accounts")


@app.route('/transactions')
def transactions_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    transactions = sqlsession.query(Transaction, Category, Business, Account).\
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
    transaction = sqlsession.query(Transaction).\
                    filter(Transaction.transno == transno).\
                    one()
    businesses = sqlsession.query(Business).\
                    filter(Business.username == session['user']).\
                    all()
    categories = sqlsession.query(Category).\
                    filter(Category.username == session['user']).\
                    all()
    accounts = sqlsession.query(Account).\
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

            sqlsession.add(transaction)
            sqlsession.commit()

        if request.form['submit'] == 'Delete':
            sqlsession.delete(transaction)
            sqlsession.commit()

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
    businesses = sqlsession.query(Business).\
                    filter(Business.username == session['user']).\
                    all()
    return render_template('businesses.html',businesses=businesses, menu="businesses")


@app.route('/categories')
def categories_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    categories = sqlsession.query(Category).\
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
