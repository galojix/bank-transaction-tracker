"""Email module."""
from flask_mail import Mail
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

mail = Mail()


def send_async_email(app, msg):
    """Send an email asynchronously."""
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """Send an email."""
    app = current_app._get_current_object()
    msg = Message(
        app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread
