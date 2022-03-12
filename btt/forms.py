"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms.form import Form
from wtforms import (
    SubmitField,
    SelectField,
    FloatField,
    SelectMultipleField,
    StringField,
    FieldList,
    FormField,
    BooleanField,
)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, InputRequired
from flask_wtf.file import FileField, FileRequired
from wtforms import widgets


class ModifyTransactionForm(FlaskForm):
    """Modify transaction form."""

    date = DateTimeLocalField(
        "Date:", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    description = StringField("Description:", validators=[DataRequired()])
    category_name = SelectField("Category Name:", validators=[DataRequired()])
    account_name = SelectField("Account Name:", validators=[DataRequired()])
    amount = FloatField("Amount:", validators=[InputRequired()])
    modify = SubmitField("Modify")
    delete = SubmitField("Delete")
    cancel = SubmitField("Cancel")


class AddTransactionForm(FlaskForm):
    """Add transaction form."""

    date = DateTimeLocalField(
        "Date:", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    description = StringField("Description:", validators=[DataRequired()])
    category_name = SelectField("Category Name:", validators=[DataRequired()])
    account_name = SelectField("Account Name:", validators=[DataRequired()])
    amount = FloatField("Amount:", validators=[InputRequired()])
    add = SubmitField("Add")
    cancel = SubmitField("Cancel")


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
        "Start Date:", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    end_date = DateTimeLocalField(
        "End Date:", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    description = StringField("Description contains (optional):")
    category_names_selectall = BooleanField(
        "Select/Unselect All", default=True
    )
    category_names = MultiCheckboxField(
        "Category Names:", validators=[DataRequired()]
    )
    category_types_selectall = BooleanField(
        "Select/Unselect All", default=True
    )
    category_types = MultiCheckboxField(
        "Category Types:", validators=[DataRequired()]
    )
    account_names_selectall = BooleanField("Select/Unselect All", default=True)
    account_names = MultiCheckboxField(
        "Account Names:", validators=[DataRequired()]
    )
    search = SubmitField("Search")
    cancel = SubmitField("Cancel")


class UploadTransactionsForm(FlaskForm):
    """Upload transactions form."""

    transactions_file = FileField("File:", validators=[FileRequired()])
    account = SelectField("Account:", validators=[DataRequired()])
    upload = SubmitField("Upload")


class AddAccountForm(FlaskForm):
    """Add account form."""

    account_name = StringField("Account Name:", validators=[DataRequired()])
    add = SubmitField("Add")
    cancel = SubmitField("Cancel")


class ModifyAccountForm(FlaskForm):
    """Modify account form."""

    account_name = StringField("Account Name:", validators=[DataRequired()])
    modify = SubmitField("Modify")
    delete = SubmitField("Delete")
    cancel = SubmitField("Cancel")


class AddCategoryForm(FlaskForm):
    """Add category form."""

    category_name = StringField("Category Name:", validators=[DataRequired()])
    category_type = SelectField("Category Type:", validators=[DataRequired()])
    add = SubmitField("Add")
    cancel = SubmitField("Cancel")


class ModifyCategoryForm(FlaskForm):
    """Modify category form."""

    category_name = StringField("Category Name:", validators=[DataRequired()])
    category_type = SelectField("Category Type:", validators=[DataRequired()])
    modify = SubmitField("Modify")
    delete = SubmitField("Delete")
    cancel = SubmitField("Cancel")


class ClassifyTransactionColumnsForm(Form):
    """Classify transaction columns form."""

    column_label = SelectField(
        "Define column:", validators=[DataRequired()], choices=[]
    )


class ClassifyTransactionRowsForm(Form):
    """Classify transaction rows form."""

    category_name = SelectField("", validators=[DataRequired()])
    action = SelectField("", validators=[DataRequired()])


class ProcessUploadedTransactionsForm(FlaskForm):
    """Process uploaded transactions form."""

    col_classifications = FieldList(FormField(ClassifyTransactionColumnsForm))
    row_classifications = FieldList(FormField(ClassifyTransactionRowsForm))
    add = SubmitField("Proceed")
    cancel = SubmitField("Cancel")
    date_format = SelectField("Date Format:", validators=[DataRequired()])


class ReportForm(FlaskForm):
    """Report form."""

    start_date = DateTimeLocalField(
        "Start Date:", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    end_date = DateTimeLocalField(
        "End Date:", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    account_name = SelectField("Account Name:", validators=[DataRequired()])
    refresh = SubmitField("Refresh")
