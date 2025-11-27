from flask import Flask, render_template

from .blueprints import auth_bp
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

    from app import models  # noqa: F401

    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return render_template("base.html")

    return app
