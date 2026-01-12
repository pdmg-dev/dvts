import os

from flask import current_app, render_template, request
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.voucher import Attachment, DisbursementVoucher

from . import voucher_bp
from .forms import DVForm


@voucher_bp.route("vouchers/")
@login_required
def all_vouchers():
    total_vouchers = DisbursementVoucher.query.count()
    # Pagination setup
    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.order_by(DisbursementVoucher.date_received.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

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
    vouchers = DisbursementVoucher.query.order_by(DisbursementVoucher.date_received.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

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
        return render_template("fragments/form_card.html", form=form, voucher=None)

    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.order_by(DisbursementVoucher.date_received.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

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

    current_app.logger.info(f"Category ID received: {form.category_id.data} ")

    voucher = DisbursementVoucher(
        date_received=form.date_received.data,
        category_id=form.category_id.data,
        mode_of_payment=form.mode_of_payment.data,
        dv_number=form.dv_number.data,
        payee=form.payee.data,
        obr_number=form.obr_number.data.strip() or None,
        address=form.address.data,
        resp_center_id=form.resp_center_id.data,
        particulars=form.particulars.data,
        amount=form.amount.data,
    )

    db.session.add(voucher)
    db.session.flush()

    files = request.files.getlist("attachments")

    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join("uploads", filename)
            file.save(filepath)

            att = Attachment(filename=filename, filepath=filepath, voucher_id=voucher.id)
            db.session.add(att)

    db.session.commit()

    fresh_form = DVForm(formdata=None)
    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = DisbursementVoucher.query.order_by(DisbursementVoucher.date_received.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template("partials/form.html", voucher=voucher, form=fresh_form, vouchers=vouchers)
    # return "", 200, {"HX-Retarget": "#floatingCardContainer", "HX-Reswap": "innerHTML"}


@voucher_bp.post("/voucher/<int:voucher_id>/attachments")
@login_required
def upload_attachment(voucher_id):
    current_app.logger.info("UPLOAD ROUTE CALLED")

    file = request.files.get("file")
    if not file:
        return "No file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    attach = Attachment(voucher_id=voucher_id, filename=filename)
    db.session.add(attach)
    db.session.commit()

    attachments = Attachment.query.filter_by(voucher_id=voucher_id).all()
    return render_template("partials/attachment_items.html", attachments=attachments)


@voucher_bp.delete("/attachment/<int:attachment_id>")
@login_required
def delete_attachment(attachment_id):
    a = Attachment.query.get_or_404(attachment_id)
    db.session.delete(a)
    db.session.commit()
    return ""  # HTMX will remove the list item
