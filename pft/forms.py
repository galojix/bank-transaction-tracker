"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, SelectField, FloatField)
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
