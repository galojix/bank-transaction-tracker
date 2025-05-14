"""Module that handles the authorization forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    PasswordField,
    BooleanField,
    ValidationError,
    RadioField,
)
from wtforms.validators import Length, Email, EqualTo, DataRequired
from ..database import User
from ..forms import MultiCheckboxField


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(4, 64)]
    )
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    """User registration form."""

    email_validators = [DataRequired(), Length(1, 64), Email()]
    email = StringField("Email", validators=email_validators)
    password_validators = [
        DataRequired(),
        EqualTo("password2", message="Passwords must match."),
        Length(4, 64),
    ]
    password = PasswordField("Password", validators=password_validators)
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        """Validate email address."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")


class ChangePasswordForm(FlaskForm):
    """Change password form."""

    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
            Length(4, 64),
        ],
    )
    password2 = PasswordField(
        "Confirm new password", validators=[DataRequired()]
    )
    submit = SubmitField("Update Password")


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form."""

    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    """Password reset form."""

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match"),
            Length(4, 64),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    """Change email form."""

    email = StringField(
        "New Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(4, 64)]
    )
    submit = SubmitField("Update Email Address")

    def validate_email(self, field):
        """Validate email address."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")


class DeleteUserForm(FlaskForm):
    """Delete user form."""

    yes = SubmitField("Yes")
    no = SubmitField("No")


class ChangeGroupForm(FlaskForm):
    """Change group form."""

    groups = RadioField("", validators=[DataRequired()])
    submit = SubmitField("Submit")
    cancel = SubmitField("Cancel")


class ModifyGroupNameForm(FlaskForm):
    """Modify group form."""

    group_name = StringField("Group Name:", validators=[DataRequired()])
    modify = SubmitField("Modify")
    cancel = SubmitField("Cancel")


class DeleteGroupMemberForm(FlaskForm):
    """Delete group member form."""

    del_email = MultiCheckboxField("")
    delete = SubmitField("Delete")
    cancel = SubmitField("Cancel")


class AddGroupMemberForm(FlaskForm):
    """Delete group member form."""

    email_validators = [DataRequired(), Length(0, 64), Email()]
    add_email = StringField("Email:", validators=email_validators)
    add = SubmitField("Add")
    cancel = SubmitField("Cancel")
