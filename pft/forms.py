"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, SelectField, FloatField, SelectMultipleField)
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, InputRequired


class ModifyTransactionForm(FlaskForm):
    """Modify transaction form."""

    date = DateTimeLocalField(
        'Date:', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    business_name = SelectField('Business Name:', validators=[DataRequired()])
    category_name = SelectField('Category Name:', validators=[DataRequired()])
    account_name = SelectField('Account Name:', validators=[DataRequired()])
    amount = FloatField('Amount:', validators=[InputRequired()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class AddTransactionForm(FlaskForm):
    """Modify transaction form."""

    date = DateTimeLocalField(
        'Date:', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    business_name = SelectField('Business Name:', validators=[DataRequired()])
    category_name = SelectField('Category Name:', validators=[DataRequired()])
    account_name = SelectField('Account Name:', validators=[DataRequired()])
    amount = FloatField('Amount:', validators=[InputRequired()])
    add = SubmitField('Add')
    cancel = SubmitField('Cancel')


class SearchTransactionsForm(FlaskForm):
    """Modify transaction form."""

    start_date = DateTimeLocalField(
        'Date:', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField(
        'Date:', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    category_names = SelectMultipleField(
        'Category Name:', validators=[DataRequired()])
    category_types = SelectMultipleField(
        'Category Types:', validators=[DataRequired()])
    business_names = SelectMultipleField(
        'Business Name:', validators=[DataRequired()])
    account_names = SelectMultipleField(
        'Account Name:', validators=[DataRequired()])
    search = SubmitField('Search')
    cancel = SubmitField('Cancel')
