"""Module that handles web views."""
from flask import render_template, url_for, request, redirect, session, flash,\
    Blueprint
# from datetime import datetime
# from sqlalchemy.orm.exc import NoResultFound
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
from .database import Transaction, Category, Business, Account, User
from .forms import ModifyTransactionForm, LoginForm, RegistrationForm
from .database import db
from .reports import graph


web = Blueprint('web', __name__)


@web.route('/home')
@login_required
def home_page():
    """Return Home HTML page."""
    return render_template('home.html', user=current_user.username,
                           login_time=session.get('login_time'), menu="home")


@web.route('/', methods=['GET', 'POST'])
@web.route('/login', methods=['GET', 'POST'])
def login():
    """Login and return home page."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or
                            url_for('web.home_page'))
        flash('Invalid username or password.')
    session['login_time'] = datetime.utcnow()
    return render_template('login.html', form=form)


@web.route('/logout')
def logout():
    """Log out and return login form."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('web.login'))


@web.route('/register', methods=['GET', 'POST'])
def register():
    """User registration form."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        # Add default categories
        user.add_category(catname="Unspecified Expense", cattype="Expense")
        user.add_category(catname="Unspecified Income", cattype="Income")
        # Add default account
        user.add_account(accname="Unknown", balance=0)
        # Add default business
        user.add_business(busname="Unknown")
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('web.login'))
    return render_template('register.html', form=form)


@web.route('/accounts')
@login_required
def accounts_page():
    """Return Accounts HTML page."""
    accounts = db.session.query(Account).\
        filter(Account.username == current_user.username).all()
    return render_template('accounts.html', accounts=accounts, menu="accounts")


@web.route('/transactions')
@login_required
def transactions_page():
    """Return Transactions HTML page."""
    transactions = db.session.query(Transaction, Category, Business, Account).\
        filter(Transaction.username == current_user.username).\
        filter(Transaction.catno == Category.catno).\
        filter(Transaction.busno == Business.busno).\
        filter(Transaction.accno == Account.accno).\
        all()
    return render_template('transactions.html', transactions=transactions,
                           menu="transactions")


@web.route('/transactions/modify/<int:transno>/', methods=['GET', 'POST'])
@login_required
def modify_transaction(transno):
    """
    Modify or delete transactions.

    Return a form for modifying transactions or process submitted
    form and redirect to Transactions HTML page.
    """
    transaction = db.session.query(Transaction).\
        filter(Transaction.transno == transno).\
        one()
    businesses = db.session.query(Business).\
        filter(Business.username == current_user.username).\
        all()
    categories = db.session.query(Category).\
        filter(Category.username == current_user.username).\
        all()
    accounts = db.session.query(Account).\
        filter(Account.username == current_user.username).\
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

    return render_template('modify_transaction.html', form=form,
                           transno=transaction.transno, menu="transactions")


@web.route('/businesses')
@login_required
def businesses_page():
    """Return Businesses HTML page."""
    businesses = db.session.query(Business).\
        filter(Business.username == current_user.username).all()
    return render_template('businesses.html', businesses=businesses,
                           menu="businesses")


@web.route('/categories')
@login_required
def categories_page():
    """Return Categories HTML page."""
    categories = db.session.query(Category).\
        filter(Category.username == current_user.username).all()
    return render_template('categories.html', categories=categories,
                           menu="categories")


@web.route('/reports/<report_name>/')
@login_required
def reports_page(report_name):
    """Return reports HTML page."""
    return render_template('reports.html', graph=graph(report_name),
                           menu="reports")
