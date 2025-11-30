from flask import render_template, request

from app.models.voucher import DisbursementVoucher

from . import voucher_bp


@voucher_bp.route("/")
def all_vouchers():
    total_vouchers = DisbursementVoucher.query.count()

    # Pagination setup
    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)

    # Item numbers for pagination (first and last on the current page)
    first_item = (vouchers.page - 1) * vouchers.per_page + 1
    last_item = min(vouchers.page * vouchers.per_page, vouchers.total)

    template = "vouchers_partials.html" if request.headers.get("HX-Request") else "vouchers.html"

    return render_template(
        template,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        first_item=first_item,
        last_item=last_item,
    )


@voucher_bp.route("/<int:voucher_id>")
def view_voucher(voucher_id):
    voucher = DisbursementVoucher.query.get_or_404(voucher_id)
    total_vouchers = DisbursementVoucher.query.count()

    # Pagination setup
    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)

    # Calculate the item number of the current voucher
    current_voucher = (
        DisbursementVoucher.query.order_by(DisbursementVoucher.id).filter(DisbursementVoucher.id <= voucher_id).count()
    )

    # Get next and previous vouchers
    next_voucher = (
        DisbursementVoucher.query.order_by(DisbursementVoucher.id).filter(DisbursementVoucher.id > voucher_id).first()
    )
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
        template = "vouchers.html"

    return render_template(
        template,
        voucher=voucher,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        current_voucher=current_voucher,
        next_voucher=next_voucher,
        prev_voucher=prev_voucher,
    )
