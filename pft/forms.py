"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, SelectField, FloatField, SelectMultipleField)
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, InputRequired
from wtforms import widgets


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


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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
    account_names = MultiCheckboxField(
        'Account Name:', validators=[DataRequired()])
    search = SubmitField('Search')
    cancel = SubmitField('Cancel')
