"""Module that creates and initialises application."""
import logging
import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate
# from flask_paranoid import Paranoid
from logging.handlers import SMTPHandler, RotatingFileHandler
from .database import db, User
from .views import web
from .errors import error
from .auth.views import auth
from config import config
from .email import mail


sess = Session()
bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
migrate = Migrate()
# paranoid = Paranoid()


@login_manager.user_loader
def load_user(user_id):
    """Load a user for Flask-Login."""
    return User.query.get(int(user_id))


def create_app(config_name):
    """Create Flask app."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    sess.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    app.register_blueprint(web)
    app.register_blueprint(error)
    app.register_blueprint(auth)
    # paranoid.init_app(app)
    # paranoid.redirect_view = '/'
    if not app.debug:
        if app.config['MAIL_SERVER']:
            authentication = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                authentication = (
                    app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='PFT Failure',
                credentials=authentication, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
            file_handler = RotatingFileHandler(
                'logs/btt.log', maxBytes=10240, backupCount=10)
            formatter = (
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
            )
            file_handler.setFormatter(logging.Formatter(formatter))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('PFT startup')
    return app
