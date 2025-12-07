from flask import Flask, redirect, url_for

from .blueprints import admin_bp, auth_bp, voucher_bp
from .config import get_config
from .extensions import bcrypt, db, login_manager, migrate, socketio
from .filters import init_filters


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

    # Register custom Jinja filters
    init_filters(app)

    from app import models  # noqa: F401

    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)
    app.register_blueprint(voucher_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        return redirect(url_for("voucher.all_vouchers"))

    return app
