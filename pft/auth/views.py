"""Module that handles auth views."""
from flask import render_template, url_for, request, redirect, session, flash,\
    Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
from ..database import User
from .forms import (
    LoginForm, RegistrationForm, ChangeEmailForm, ChangePasswordForm,
    PasswordResetForm, PasswordResetRequestForm)
from ..database import db
from ..email import send_email


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
               'auth/mail/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('web.home_page'))


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
        user = User(
            name=form.name.data, email=form.email.data,
            password=form.password.data)
        # Add default categories
        user.add_category(catname="Unspecified Expense", cattype="Expense")
        user.add_category(catname="Unspecified Income", cattype="Income")
        user.add_category(
            catname="Transfer In", cattype="Transfer In")
        user.add_category(
            catname="Transfer Out", cattype="Transfer Out")
        # Add default account
        user.add_account(accname="Unknown", balance=0)
        # Add default business
        user.add_business(busname="Unknown")
        db.session.add(user)

        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email, 'Confirm Your Account', 'auth/mail/confirm',
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


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('web.home_page'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """Password reset request."""
    if not current_user.is_anonymous:
        return redirect(url_for('web.home_page'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/mail/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Password reset."""
    if not current_user.is_anonymous:
        return redirect(url_for('web.home_page'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('web.home_page'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Change email request."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/mail/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('web.home_page'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    """Change email."""
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('web.home_page'))
