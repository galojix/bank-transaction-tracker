"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, FloatField, StringField,\
    PasswordField, BooleanField, ValidationError
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from .database import User


class ModifyTransactionForm(FlaskForm):
    """Class that instantiates a form for modifying transactions."""

    date = DateTimeLocalField('Date:', format='%Y-%m-%dT%H:%M',
                              validators=[Required()])
    business_name = SelectField('Business Name:', validators=[Required()])
    category_name = SelectField('Category Name:', validators=[Required()])
    account_name = SelectField('Account Name:', validators=[Required()])
    amount = FloatField('Amount:', validators=[Required()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """User registration form."""

    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        """Validate email address."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """Validate username."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
