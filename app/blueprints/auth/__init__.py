from flask import Blueprint

from app.extensions import login_manager
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

from . import forms, routes  # noqa: E402 F401


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
