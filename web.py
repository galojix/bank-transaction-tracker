from flask import Flask, render_template
from database_setup import User, Transaction, Category, Business, Account, session

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home_page():
    transactions = session.query(Transaction, Category, Business, Account).\
                           filter(Transaction.catno == Category.catno).\
                           filter(Transaction.busno == Business.busno).\
                           filter(Transaction.accno == Account.accno).\
                           all()
    return render_template('home.xhtml',transactions=transactions, menu="home")


@app.route('/accounts')
def accounts_page():
    accounts = session.query(Account).all()
    return render_template('accounts.xhtml',accounts=accounts, menu="accounts")


@app.route('/transactions')
def transactions_page():
    transactions = session.query(Transaction, Category, Business, Account).\
                           filter(Transaction.catno == Category.catno).\
                           filter(Transaction.busno == Business.busno).\
                           filter(Transaction.accno == Account.accno).\
                           all()
    return render_template('transactions.xhtml',transactions=transactions, menu="transactions")


@app.route('/businesses')
def businesses_page():
    businesses = session.query(Business).all()
    return render_template('businesses.xhtml',businesses=businesses, menu="businesses")


@app.route('/categories')
def categories_page():
    categories = session.query(Category).all()
    return render_template('categories.xhtml',categories=categories, menu="categories")


@app.route('/reports')
def reports_page():
    return render_template('reports.xhtml',menu="reports")


if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
