"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, SelectField, FloatField, SelectMultipleField, TextField,
    FieldList, FormField)
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, InputRequired
from flask_wtf.file import FileField, FileRequired
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
    """Add transaction form."""

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
        'Start Date:', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField(
        'End Date:', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    category_names = MultiCheckboxField(
        'Category Names:', validators=[DataRequired()])
    category_types = MultiCheckboxField(
        'Category Types:', validators=[DataRequired()])
    business_names = MultiCheckboxField(
        'Business Names:', validators=[DataRequired()])
    account_names = MultiCheckboxField(
        'Account Names:', validators=[DataRequired()])
    search = SubmitField('Search')
    cancel = SubmitField('Cancel')


class UploadTransactionsForm(FlaskForm):
    """Upload transactions form."""

    transactions_file = FileField('File:', validators=[FileRequired()])
    account = SelectField('Account:', validators=[DataRequired()])
    upload = SubmitField('Upload')


class AddAccountForm(FlaskForm):
    """Add account form."""

    account_name = TextField('Account Name:', validators=[DataRequired()])
    initial_balance = FloatField(
        'Initial Balance:', validators=[InputRequired()])
    add = SubmitField('Add')
    cancel = SubmitField('Cancel')


class ModifyAccountForm(FlaskForm):
    """Modify account form."""

    account_name = TextField('Account Name:', validators=[DataRequired()])
    initial_balance = FloatField(
        'Initial Balance:', validators=[InputRequired()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class AddCategoryForm(FlaskForm):
    """Add category form."""

    category_name = TextField('Account Name:', validators=[DataRequired()])
    category_type = SelectField('Category Type:', validators=[DataRequired()])
    add = SubmitField('Add')
    cancel = SubmitField('Cancel')


class ModifyCategoryForm(FlaskForm):
    """Modify category form."""

    category_name = TextField('Category Name:', validators=[DataRequired()])
    category_type = SelectField('Category Type:', validators=[DataRequired()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class AddBusinessForm(FlaskForm):
    """Add business form."""

    business_name = TextField('Business Name:', validators=[DataRequired()])
    add = SubmitField('Add')
    cancel = SubmitField('Cancel')


class ModifyBusinessForm(FlaskForm):
    """Modify business form."""

    business_name = TextField('Business Name:', validators=[DataRequired()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class ClassifyTransactionColumnsForm(FlaskForm):
    """Classify transaction columns form."""

    name = TextField()


class ProcessUploadedTransactionsForm(FlaskForm):
    """Process uploaded transactions form."""

    classifications = FieldList(
        FormField(ClassifyTransactionColumnsForm), min_entries=1)
