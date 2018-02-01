"""Module that handles web views."""
from flask import render_template, url_for, redirect, session, Blueprint
from flask_login import login_required, current_user
from .database import Transaction, Category, Business, Account
from .forms import ModifyTransactionForm
from .database import db
from .reports import graph


web = Blueprint('web', __name__)


@web.route('/home')
@login_required
def home_page():
    """Return Home HTML page."""
    return render_template(
        'home.html', user=current_user.email,
        login_time=session.get('login_time'), menu="home")


@web.route('/accounts')
@login_required
def accounts_page():
    """Return Accounts HTML page."""
    accounts = (
        db.session.query(Account)
        .filter(Account.id == current_user.id).all())
    return render_template('accounts.html', accounts=accounts, menu="accounts")


@web.route('/accounts/modify/<int:accno>/', methods=['GET', 'POST'])
@login_required
def modify_account(accno):
    """
    Modify or delete accounts.

    Return a form for modifying accounts or process submitted
    form and redirect to Accounts HTML page.
    """
    return redirect(url_for('.accounts_page'))


@web.route('/transactions')
@login_required
def transactions_page():
    """Return Transactions HTML page."""
    transactions = (
        db.session.query(Transaction, Category, Business, Account)
        .filter(Transaction.id == current_user.id)
        .filter(Transaction.catno == Category.catno)
        .filter(Transaction.busno == Business.busno)
        .filter(Transaction.accno == Account.accno)
        .order_by(Transaction.date)
        .all())
    return render_template(
        'transactions.html', transactions=transactions, menu="transactions")


@web.route('/transactions/modify/<int:transno>/', methods=['GET', 'POST'])
@login_required
def modify_transaction(transno):
    """
    Modify or delete transactions.

    Return a form for modifying transactions or process submitted
    form and redirect to Transactions HTML page.
    """
    transaction = (
        db.session.query(Transaction)
        .filter(Transaction.transno == transno)
        .filter(Transaction.id == current_user.id)
        .one())
    businesses = transaction.user.businesses
    categories = transaction.user.categories
    accounts = transaction.user.accounts

    business_names = [
        (business.busname, business.busname) for business in businesses]
    category_names = [
        (category.catname, category.catname) for category in categories]
    account_names = [
        (account.accname, account.accname) for account in accounts]

    form = ModifyTransactionForm()
    form.date.default = transaction.date
    form.business_name.choices = business_names
    form.business_name.default = transaction.business.busname
    form.category_name.choices = category_names
    form.category_name.default = transaction.category.catname
    form.account_name.choices = account_names
    form.account_name.default = transaction.account.accname
    form.amount.default = '{:,.2f}'.format(transaction.amount / 100)

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
            transaction.amount = form.amount.data * 100
            db.session.add(transaction)
            db.session.commit()
        elif form.delete.data:
            db.session.delete(transaction)
            db.session.commit()
        elif form.cancel.data:
            pass
        return redirect(url_for('.transactions_page'))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template(
        'modify_transaction.html', form=form, transno=transaction.transno,
        menu="transactions")


@web.route('/businesses')
@login_required
def businesses_page():
    """Return Businesses HTML page."""
    businesses = (
        db.session.query(Business)
        .filter(Business.id == current_user.id).all())
    return render_template('businesses.html', businesses=businesses,
                           menu="businesses")


@web.route('/businesses/modify/<int:busno>/', methods=['GET', 'POST'])
@login_required
def modify_business(busno):
    """
    Modify or delete businesses.

    Return a form for modifying businesses or process submitted
    form and redirect to Businesses HTML page.
    """
    return redirect(url_for('.businesses_page'))


@web.route('/categories')
@login_required
def categories_page():
    """Return Categories HTML page."""
    categories = (
        db.session.query(Category)
        .filter(Category.id == current_user.id).all())
    return render_template(
        'categories.html', categories=categories, menu="categories")


@web.route('/categories/modify/<int:catno>/', methods=['GET', 'POST'])
@login_required
def modify_category(catno):
    """
    Modify or delete categories.

    Return a form for modifying categories or process submitted
    form and redirect to Categories HTML page.
    """
    return redirect(url_for('.categories_page'))


@web.route('/reports/<report_name>/')
@login_required
def reports_page(report_name):
    """Return reports HTML page."""
    return render_template(
        'reports.html', report_name=report_name, graph=graph(report_name),
        menu="reports")
