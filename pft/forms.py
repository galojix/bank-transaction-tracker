"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, SelectField, FloatField)
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import Required, DataRequired


class ModifyTransactionForm(FlaskForm):
    """Modify transaction form."""

    date = DateTimeLocalField(
        'Date:', format='%Y-%m-%dT%H:%M', validators=[Required()])
    business_name = SelectField('Business Name:', validators=[Required()])
    category_name = SelectField('Category Name:', validators=[Required()])
    account_name = SelectField('Account Name:', validators=[Required()])
    amount = FloatField('Amount:', validators=[DataRequired()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')
