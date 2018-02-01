"""Module that handles auth views."""
from flask import render_template, url_for, request, redirect, session, flash,\
    Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
from .database import User
from .forms import LoginForm, RegistrationForm
from .database import db
from .email import send_email


auth = Blueprint('auth', __name__)


@auth.before_app_request
def before_request():
    """Check user is confirmed before every request."""
    if current_user.is_authenticated:
        # current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    """User is unconfirmed."""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('web.home_page'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """Resend account confirmation."""
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'mail/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('web.home_page'))


@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login and return home page."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(
                request.args.get('next') or url_for('web.home_page'))
        flash('Invalid email or password.')
    session['login_time'] = datetime.utcnow()
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    """Log out and return login form."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration form."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    password=form.password.data)
        # Add default categories
        user.add_category(catname="Unspecified Expense", cattype="Expense")
        user.add_category(catname="Unspecified Income", cattype="Income")
        # Add default account
        user.add_account(accname="Unknown", balance=0)
        # Add default business
        user.add_business(busname="Unknown")
        db.session.add(user)

        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email, 'Confirm Your Account', 'mail/confirm',
            user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """Confirm account."""
    if current_user.confirmed:
        return redirect(url_for('web.home_page'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('web.home_page'))
