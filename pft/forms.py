"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import Required


class ModifyTransactionForm(FlaskForm):
    """Class that instantiates a form for modifying transactions."""

    date = DateTimeLocalField('Date:', format='%Y-%m-%dT%H:%M',
                              validators=[Required()])
    business_name = SelectField('Business Name:', validators=[Required()])
    category_name = SelectField('Category Name:', validators=[Required()])
    account_name = SelectField('Account Name:', validators=[Required()])
    amount = IntegerField('Amount:', validators=[Required()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')
