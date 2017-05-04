"""Module that creates and initialises application."""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from .database import db
from .views import web
from .errors import error
from config import config


bootstrap = Bootstrap()
moment = Moment()


def create_app(config_name):
    """Create Flask app."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    app.register_blueprint(web)
    app.register_blueprint(error)
    return app
