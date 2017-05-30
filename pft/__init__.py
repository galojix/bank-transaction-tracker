"""Module that creates and initialises application."""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from .database import db, User
from .views import web
from .errors import error
from config import config


bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(username):
    """Callback function for Flask-Login that loads a User."""
    return User.query.get(username)


def create_app(config_name):
    """Create Flask app."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(web)
    app.register_blueprint(error)
    return app
