from flask import render_template, request

from app.models.voucher import DisbursementVoucher

from . import voucher_bp


@voucher_bp.route("/")
def all_vouchers():
    page = request.args.get("page", 1, type=int)
    per_page = 25

    pagination = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)

    template = "vouchers_partials.html" if request.headers.get("HX-Request") else "vouchers.html"
    return render_template(template, pagination=pagination)
