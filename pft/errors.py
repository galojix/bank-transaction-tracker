"""Module that contains error handlers."""
from flask import render_template, Blueprint
from .database import db

error = Blueprint('error', __name__)


@error.app_errorhandler(404)
def page_not_found(e):
    """Return page not found HTML page."""
    return render_template('404.html'), 404


@error.app_errorhandler(500)
def internal_server_error(e):
    """Return internal server error HTML page."""
    db.session.rollback()
    return render_template('500.html'), 500
