"""Module that initialises application."""
from flask import Flask
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from .database import db
from .views import web


app = Flask(__name__)
app.config.from_object('config')
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db.init_app(app)
app.register_blueprint(web)
