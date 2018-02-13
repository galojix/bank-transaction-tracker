"""Module that handles web views."""
from flask import render_template, url_for, redirect, session, Blueprint
from flask_login import login_required, current_user
from .database import Transaction
from .forms import (
    ModifyTransactionForm, AddTransactionForm, SearchTransactionsForm,
    UploadTransactionsForm)
from werkzeug import secure_filename
from .database import db
from .reports import graph
import datetime


web = Blueprint('web', __name__)


@web.route('/')
@web.route('/home')
def home_page():
    """Return Home HTML page."""
    return render_template(
        'home.html', current_user=current_user,
        login_time=session.get('login_time'), menu="home")


@web.route('/accounts')
@login_required
def accounts_page():
    """Return Accounts HTML page."""
    accounts = current_user.accounts
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
    transactions = current_user.transactions
    transaction_numbers = session.get('transactions')
    if transaction_numbers:
        transactions = [
            transaction for transaction in transactions
            if transaction.transno in transaction_numbers]
    return render_template(
        'transactions.html', transactions=transactions,
        menu="transactions")


@web.route('/transactions/search', methods=['GET', 'POST'])
@login_required
def search_transactions():
    """
    Search for transactions.

    Return a form for searching transactions or process submitted
    form and render Transactions HTML page.
    """
    businesses = current_user.businesses
    categories = current_user.categories
    category_types = {category.cattype for category in categories}
    accounts = current_user.accounts

    form = SearchTransactionsForm()

    # Form choices and defaults
    form.start_date.default = current_user.transactions[0].date
    form.end_date.default = datetime.datetime.now()
    form.category_names.choices = [
        (category.catname, category.catname) for category in categories]
    form.category_names.default = [category.catname for category in categories]
    form.category_types.choices = [
        (category_type, category_type) for category_type in category_types]
    form.category_types.default = [
        category_type for category_type in category_types]
    form.business_names.choices = [
        (business.busname, business.busname) for business in businesses]
    form.business_names.default = [business.busname for business in businesses]
    form.account_names.choices = [
        (account.accname, account.accname) for account in accounts]
    form.account_names.default = [account.accname for account in accounts]

    if form.validate_on_submit():
        # This must go here or else before_app_request will try to commit
        # transaction with NULL fields when SQLALCHEMY_COMMIT_ON_TEARDOWN
        # is set to True
        if form.search.data:
            start_date = form.start_date.data
            end_date = form.end_date.data
            category_names = form.category_names.data
            category_types = form.category_types.data
            business_names = form.business_names.data
            account_names = form.account_names.data
            transactions = current_user.transactions
            selected_transactions = []
            for transaction in transactions:
                if (
                    transaction.date >= start_date
                    and transaction.date <= end_date
                    and transaction.category.catname in category_names
                    and transaction.category.cattype in category_types
                    and transaction.business.busname in business_names
                    and transaction.account.accname in account_names
                ):
                    selected_transactions.append(transaction)
        elif form.cancel.data:
            selected_transactions = current_user.transactions

        session['transactions'] = [
            transaction.transno for transaction in selected_transactions]

        return redirect(url_for('.transactions_page'))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template(
        'search_transactions.html', form=form, menu="transactions")


@web.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """
    Add a transaction.

    Return a form for adding a transaction or process submitted
    form and redirect to Transactions HTML page.
    """
    businesses = current_user.businesses
    categories = current_user.categories
    accounts = current_user.accounts

    business_names = [
        (business.busname, business.busname) for business in businesses]
    category_names = [
        (category.catname, category.catname) for category in categories]
    account_names = [
        (account.accname, account.accname) for account in accounts]

    form = AddTransactionForm()
    form.date.default = datetime.datetime.now()
    form.business_name.choices = business_names
    form.business_name.default = business_names[0]
    form.category_name.choices = category_names
    form.category_name.default = category_names[0]
    form.account_name.choices = account_names
    form.account_name.default = account_names[0]
    form.amount.default = '{:,.2f}'.format(0)
    #
    if form.validate_on_submit():
        # This must go here or else before_app_request will try to commit
        # transaction with NULL fields when SQLALCHEMY_COMMIT_ON_TEARDOWN
        # is set to True
        transaction = Transaction(user=current_user)
        if form.add.data:
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
        elif form.cancel.data:
            db.session.rollback()
        # Clear search parameters
        if 'transactions' in session:
            del session['transactions']
        return redirect(url_for('.transactions_page'))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template(
        'add_transaction.html', form=form, menu="transactions")


@web.route('/transactions/modify/<int:transno>/', methods=['GET', 'POST'])
@login_required
def modify_transaction(transno):
    """
    Modify or delete transactions.

    Return a form for modifying transactions or process submitted
    form and redirect to Transactions HTML page.
    """
    transaction = (
        Transaction.query.filter_by(user=current_user, transno=transno).one())
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


@web.route('/transactions/upload', methods=['GET', 'POST'])
@login_required
def upload_transactions():
    """
    Upload transactions.

    Return a form for uploading transactions or process submitted
    form and redirect to Transactions HTML page.
    """
    form = UploadTransactionsForm()
    accounts = current_user.accounts
    account_names = [
        (account.accname, account.accname) for account in accounts]
    form.account.choices = account_names
    form.account.default = accounts[0].accname

    if form.validate_on_submit():
        if form.upload.data:
            filename = secure_filename(form.transactions_file.data.filename)
            form.transactions_file.data.save('uploads/' + filename)
        return redirect(url_for('.transactions_page'))

    return render_template('upload_transactions.html', form=form)


@web.route('/businesses')
@login_required
def businesses_page():
    """Return Businesses HTML page."""
    businesses = current_user.businesses
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
    categories = current_user.categories
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
