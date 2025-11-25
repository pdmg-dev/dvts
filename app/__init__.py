from flask import Flask

from .config import get_config
from .extensions import bcrypt, db, login_manager, migrate, socketio


def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class())
    else:
        app.config.from_object(get_config())

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)

    return app
