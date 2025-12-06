from flask import Blueprint

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
    static_url_path="/admin/static",
)

from . import forms, routes  # noqa: E402 F401
