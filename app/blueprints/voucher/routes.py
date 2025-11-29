from flask import render_template, request

from app.models.voucher import DisbursementVoucher

from . import voucher_bp


@voucher_bp.route("/")
def all_vouchers():
    page = request.args.get("page", 1, type=int)
    per_page = 25

    pagination = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)
    total_vouchers = DisbursementVoucher.query.count()

    template = "vouchers_partials.html" if request.headers.get("HX-Request") else "vouchers.html"
    return render_template(template, pagination=pagination, total_vouchers=total_vouchers)


@voucher_bp.route("/<int:voucher_id>")
def view_voucher(voucher_id):
    voucher_number = request.args.get("voucher_number")  # Fetch the voucher_number

    voucher = DisbursementVoucher.query.get(voucher_id)
    page = request.args.get("page", 1, type=int)
    per_page = 25

    pagination = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)
    total_vouchers = DisbursementVoucher.query.count()

    template = "voucher_partials.html" if request.headers.get("HX-Request") else "voucher.html"
    return render_template(
        template, voucher=voucher, pagination=pagination, total_vouchers=total_vouchers, voucher_number=voucher_number
    )
