"""Module that creates and initialises application."""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from .database import db, User
from .views import web
from .errors import error
from .auths import auth
from config import config
from .email import mail


bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    """Load a user for Flask-Login."""
    return User.query.get(user_id)


def create_app(config_name):
    """Create Flask app."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    app.register_blueprint(web)
    app.register_blueprint(error)
    app.register_blueprint(auth)
    return app
