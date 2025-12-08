from flask import render_template, request
from flask_login import login_required

from app.extensions import db
from app.models.voucher import DisbursementVoucher

from . import voucher_bp
from .forms import DVForm


@voucher_bp.route("vouchers/")
@login_required
def all_vouchers():
    total_vouchers = DisbursementVoucher.query.count()
    # Pagination setup
    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)

    # Item numbers for pagination (first and last on the current page)
    first_item = (vouchers.page - 1) * vouchers.per_page + 1
    last_item = min(vouchers.page * vouchers.per_page, vouchers.total)

    template = "fragments/list_content.html" if request.headers.get("HX-Request") else "pages/list.html"

    return render_template(
        template,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        first_item=first_item,
        last_item=last_item,
    )


@voucher_bp.route("voucher/<int:voucher_id>")
@login_required
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
            template = "partials/detail.html"
        else:
            template = "fragments/detail_content.html"
    else:
        template = "pages/detail.html"

    return render_template(
        template,
        voucher=voucher,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        current_voucher=current_voucher,
        next_voucher=next_voucher,
        prev_voucher=prev_voucher,
    )


@voucher_bp.route("/voucher/new")
@login_required
def new_voucher():
    form = DVForm()
    if request.headers.get("HX-Request"):
        return render_template("fragments/form_card.html", form=form)

    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)

    total_vouchers = vouchers.total
    first_item = (vouchers.page - 1) * vouchers.per_page + 1
    last_item = min(vouchers.page * vouchers.per_page, vouchers.total)

    template = "pages/list.html"
    return render_template(
        template,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        first_item=first_item,
        last_item=last_item,
        form=form,
        show_card=True,
    )


@voucher_bp.route("/voucher/save", methods=["POST"])
@login_required
def save_voucher():
    form = DVForm()

    if not form.validate_on_submit():
        return render_template("partials/form.html", form=form)

    existing = DisbursementVoucher.query.filter_by(obr_number=form.obr_number.data).first()
    if existing:
        form.obr_number.errors.append("OBR number already exists")
        return render_template("partials/form.html", form=form)

    voucher = DisbursementVoucher(
        date_received=form.date_received.data,
        category=form.category.data,
        mode_of_payment=form.mode_of_payment.data,
        dv_number=form.dv_number.data,
        payee=form.payee.data,
        obr_number=form.obr_number.data.strip() or None,
        address=form.address.data,
        resp_center=form.resp_center.data,
        particulars=form.particulars.data,
        amount=form.amount.data,
    )

    db.session.add(voucher)
    db.session.commit()

    fresh_form = DVForm(formdata=None)
    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("partials/form.html", voucher=voucher, form=fresh_form, vouchers=vouchers)
