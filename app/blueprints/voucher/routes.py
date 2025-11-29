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
    voucher = DisbursementVoucher.query.get_or_404(voucher_id)

    # Item number
    item_number = (
        DisbursementVoucher.query.order_by(DisbursementVoucher.id).filter(DisbursementVoucher.id <= voucher_id).count()
    )
    total_vouchers = DisbursementVoucher.query.count()

    # Next voucher (if any)
    next_voucher = (
        DisbursementVoucher.query.order_by(DisbursementVoucher.id).filter(DisbursementVoucher.id > voucher_id).first()
    )

    # Previous voucher (if any)
    prev_voucher = (
        DisbursementVoucher.query.order_by(DisbursementVoucher.id.desc())
        .filter(DisbursementVoucher.id < voucher_id)
        .first()
    )

    if request.headers.get("HX-Request"):
        layout = request.headers.get("HX-Layout")
        if layout == "split":
            template = "voucher_detail.html"
        else:
            template = "voucher_partials.html"
    else:
        template = "voucher.html"

    return render_template(
        template,
        voucher=voucher,
        item_number=item_number,
        total_vouchers=total_vouchers,
        next_voucher=next_voucher,
        prev_voucher=prev_voucher,
    )
