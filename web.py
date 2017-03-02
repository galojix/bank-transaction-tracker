from flask import Flask, render_template, url_for, request, redirect
from database_setup import User, Transaction, Category, Business, Account, session
import dateutil.parser


app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home_page():
    transactions = session.query(Transaction, Category, Business, Account).\
                           filter(Transaction.catno == Category.catno).\
                           filter(Transaction.busno == Business.busno).\
                           filter(Transaction.accno == Account.accno).\
                           all()
    return render_template('home.html',transactions=transactions, menu="home")


@app.route('/accounts')
def accounts_page():
    accounts = session.query(Account).all()
    return render_template('accounts.html',accounts=accounts, menu="accounts")


@app.route('/transactions')
def transactions_page():
    transactions = session.query(Transaction, Category, Business, Account).\
                           filter(Transaction.catno == Category.catno).\
                           filter(Transaction.busno == Business.busno).\
                           filter(Transaction.accno == Account.accno).\
                           all()
    return render_template('transactions.html',transactions=transactions, menu="transactions")


@app.route('/transactions/modify/<int:transno>/', methods=['GET', 'POST'])
def modify_transaction(transno):
    transaction = session.query(Transaction).\
                    filter(Transaction.transno == transno).\
                    one()
    businesses = session.query(Business).all()
    categories = session.query(Category).all()
    accounts = session.query(Account).all()
    
    if request.method == 'POST':

        if request.form['submit'] == 'Modify':

            if request.form['date']:
                transaction.date = dateutil.parser.parse(request.form['date'])

            if request.form['amount']:
                transaction.amount = request.form['amount']

            if request.form['busName']:
                for business in businesses:
                    if business.busname == request.form['busName'] and business.username == 'demo':
                        transaction.business = business

            if request.form['catName']:
                for category in categories:
                    if category.catname == request.form['catName'] and category.username == 'demo':
                        transaction.category = category

            if request.form['accName']:
                for account in accounts:
                    if account.accname == request.form['accName'] and account.username == 'demo':
                        transaction.account = account

            session.add(transaction)
            session.commit()

        if request.form['submit'] == 'Delete':
            session.delete(transaction)
            session.commit()

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
    businesses = session.query(Business).all()
    return render_template('businesses.html',businesses=businesses, menu="businesses")


@app.route('/categories')
def categories_page():
    categories = session.query(Category).all()
    return render_template('categories.html',categories=categories, menu="categories")


@app.route('/reports')
def reports_page():
    return render_template('reports.html',menu="reports")


if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
