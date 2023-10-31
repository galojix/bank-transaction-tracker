"""Module that handles auth views."""
from urllib.parse import urlparse
from flask import (
    render_template,
    url_for,
    request,
    redirect,
    session,
    flash,
    Blueprint,
    current_app,
)
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from ..database import User, Group, MemberShip
from .forms import (
    LoginForm,
    RegistrationForm,
    ChangeEmailForm,
    ChangePasswordForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    DeleteUserForm,
    ChangeGroupForm,
    ModifyGroupNameForm,
    DeleteGroupMemberForm,
    AddGroupMemberForm,
)
from ..database import db
from ..email import send_email


auth = Blueprint("auth", __name__)


@auth.before_app_request
def before_request():
    """Check user is confirmed before every request."""
    if current_user.is_authenticated:
        # current_user.ping()
        if (
            not current_user.confirmed
            and request.endpoint
            and request.blueprint != "auth"
            and request.endpoint != "static"
        ):
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    """User is unconfirmed."""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("web.home_page"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm")
@login_required
def resend_confirmation():
    """Resend account confirmation."""
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Confirm Your Account",
        "auth/mail/confirm",
        user=current_user,
        token=token,
    )
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for("web.home_page"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Login and return home page."""
    if current_user.is_authenticated:
        return redirect(url_for("web.home_page"))
    form = LoginForm()
    app = current_app._get_current_object()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            app.logger.info("%s logged in successfully", user.email)
            session["login_time"] = datetime.utcnow()
            # Need this because login_user/remember_me is ignored
            # when using server side sessions
            session.permanent = form.remember_me.data
            next_page = request.args.get("next")
            if not next_page or urlparse(next_page).netloc != "":
                next_page = url_for("web.home_page")
            return redirect(next_page)
        app.logger.info("%s failed to log in", form.email.data)
        flash("Invalid email or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
def logout():
    """Log out and return login form."""
    app = current_app._get_current_object()
    app.logger.info("%s logged out", current_user.email)
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    """User registration form."""
    if current_user.is_authenticated:
        return redirect(url_for("web.home_page"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        group = Group(name="Group:" + form.email.data)
        group.add_categories_accounts()
        membership = MemberShip(user=user, group=group, active=True)
        db.session.add(user)
        db.session.add(group)
        db.session.add(membership)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            "Confirm Your Account",
            "auth/mail/confirm",
            user=user,
            token=token,
        )
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    """Confirm account."""
    if current_user.confirmed:
        return redirect(url_for("web.home_page"))
    if current_user.confirm(token):
        db.session.commit()
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("web.home_page"))


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash("Your password has been updated.")
            return redirect(url_for("web.home_page"))
        else:
            flash("Invalid password.")
    return render_template("auth/change_password.html", form=form)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    """Password reset request."""
    if not current_user.is_anonymous:
        return redirect(url_for("web.home_page"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                "Reset Your Password",
                "auth/mail/reset_password",
                user=user,
                token=token,
                next=request.args.get("next"),
            )
        flash(
            "An email with instructions to reset your password has been "
            "sent to you."
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    """Password reset."""
    if not current_user.is_anonymous:
        return redirect(url_for("web.home_page"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash("Your password has been updated.")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("web.home_page"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email_request():
    """Change email request."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(
                new_email,
                "Confirm your email address",
                "auth/mail/change_email",
                user=current_user,
                token=token,
            )
            flash(
                "An email with instructions to confirm your new email "
                "address has been sent to you."
            )
            return redirect(url_for("web.home_page"))
        else:
            flash("Invalid email or password.")
    return render_template("auth/change_email.html", form=form)


@auth.route("/change_email/<token>")
@login_required
def change_email(token):
    """Change email."""
    if current_user.change_email(token):
        db.session.commit()
        flash("Your email address has been updated.")
    else:
        flash("Invalid request.")
    return redirect(url_for("web.home_page"))


@auth.route("/delete_user", methods=["GET", "POST"])
@login_required
def delete_user():
    """Delete user and data."""
    form = DeleteUserForm()
    if form.validate_on_submit():
        if form.yes.data:
            for membership in current_user.memberships:
                group = membership.group
                if len(group.memberships) == 1:  # Last member of group
                    db.session.delete(group)
            db.session.delete(current_user)
            db.session.commit()
        elif form.no.data:
            pass
        return redirect(url_for("web.home_page"))
    return render_template("auth/delete_user.html", form=form, menu="home")


@auth.route("/change_group", methods=["GET", "POST"])
@login_required
def change_group():
    """Change active group."""
    form = ChangeGroupForm()
    memberships = current_user.memberships
    form.groups.choices = []
    for member in memberships:
        form.groups.choices.append((str(member.group.group_id), ""))
        if member.active:
            active_member = member
            form.groups.default = str(active_member.group.group_id)
            print(form.groups.default)
    if form.validate_on_submit():
        if form.submit.data:
            new_active_group_id = int(form.groups.data)
            active_member.active = False
            for member in memberships:
                if member.group.group_id == new_active_group_id:
                    member.active = True
            db.session.add(member)
            db.session.commit()
        elif form.cancel.data:
            pass
        return redirect(url_for("web.home_page"))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template(
        "auth/change_group.html",
        memberships=memberships,
        form=form,
        menu="myaccount",
    )


@auth.route("/modify_group_name/<int:group_id>/", methods=["GET", "POST"])
@login_required
def modify_group_name(group_id):
    """Modify group name."""
    form = ModifyGroupNameForm()
    try:
        group = (
            db.session.query(Group)
            .filter(Group.group_id == group_id)
            .filter(MemberShip.group_id == Group.group_id)
            .filter(MemberShip.id == current_user.id)
            .one()
        )
    except NoResultFound:
        flash("Invalid group.")
        return redirect(url_for("auth.change_group"))
    form.group_name.default = group.name
    if form.validate_on_submit():
        if form.modify.data:
            group.name = form.group_name.data
            db.session.add(group)
            db.session.commit()
        if form.cancel.data:
            pass
        return redirect(url_for("auth.change_group"))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template(
        "auth/modify_group_name.html", form=form, menu="myaccount"
    )


@auth.route("/delete_group_member/<int:group_id>/", methods=["GET", "POST"])
@login_required
def delete_group_member(group_id):
    """Delete group member."""
    form = DeleteGroupMemberForm()
    try:
        group = (
            db.session.query(Group)
            .filter(Group.group_id == group_id)
            .filter(MemberShip.group_id == Group.group_id)
            .filter(MemberShip.id == current_user.id)
            .one()
        )
        members = MemberShip.query.filter(
            MemberShip.group_id == group.group_id
        ).all()
    except NoResultFound:
        flash("Invalid group.")
        return redirect(url_for("auth.change_group"))
    form.del_email.choices = []
    for member in members:
        if member.user != current_user:
            email = member.user.email
            form.del_email.choices.append((email, email))
    if form.validate_on_submit():
        if form.delete.data:
            for member in members:
                if member.user.email in form.del_email.data:
                    other_membership = (
                        MemberShip.query.filter(
                            MemberShip.id == member.user.id
                        )
                        .filter(MemberShip.group_id != group.group_id)
                        .first()
                    )
                    other_membership.active = True
                    db.session.delete(member)
            db.session.commit()
        if form.cancel.data:
            pass
        return redirect(url_for("auth.change_group"))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template(
        "auth/delete_group_member.html", form=form, menu="myaccount"
    )


@auth.route("/add_group_member/<int:group_id>/", methods=["GET", "POST"])
@login_required
def add_group_member(group_id):
    """Add group member."""
    form = AddGroupMemberForm()
    try:
        group = (
            db.session.query(Group)
            .filter(Group.group_id == group_id)
            .filter(MemberShip.group_id == Group.group_id)
            .filter(MemberShip.id == current_user.id)
            .one()
        )
    except NoResultFound:
        flash("Invalid group.")
        return redirect(url_for("auth.change_group"))

    form.add_email.default = "newemail@email.com"
    if form.validate_on_submit():
        if form.add.data:
            try:
                new_user = User.query.filter_by(
                    email=form.add_email.data
                ).one()
            except NoResultFound:
                flash("Email does not belong to an existing user.")
                return redirect(url_for("auth.change_group"))
            try:
                new_member = MemberShip(
                    user=new_user, group=group, active=False
                )
                db.session.add(new_member)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Email is already a member.")
                return redirect(url_for("auth.change_group"))

        if form.cancel.data:
            pass
        return redirect(url_for("auth.change_group"))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template(
        "auth/add_group_member.html", form=form, menu="myaccount"
    )
