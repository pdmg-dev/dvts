from flask import Blueprint

voucher_bp = Blueprint("voucher", __name__, url_prefix="/vouchers", template_folder="templates")

from . import forms, routes  # noqa: E402 F401
