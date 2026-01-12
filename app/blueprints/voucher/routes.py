import os
from datetime import datetime
from io import BytesIO

from flask import current_app, render_template, request, send_file
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.voucher import Attachment, DisbursementVoucher

from . import voucher_bp
from .forms import DVForm


@voucher_bp.route("vouchers/")
@login_required
def all_vouchers():
    from app.models.voucher import Category, ResponsibilityCenter

    # Build base query
    query = DisbursementVoucher.query

    # Apply filters
    category_id = request.args.get("category", type=int)
    resp_center_id = request.args.get("resp_center", type=int)
    mode_of_payment = request.args.get("mode_of_payment")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    if category_id:
        query = query.filter(DisbursementVoucher.category_id == category_id)
    if resp_center_id:
        query = query.filter(DisbursementVoucher.resp_center_id == resp_center_id)
    if mode_of_payment:
        query = query.filter(DisbursementVoucher.mode_of_payment == mode_of_payment)
    if date_from:
        query = query.filter(DisbursementVoucher.date_received >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.filter(DisbursementVoucher.date_received <= datetime.fromisoformat(date_to))

    total_vouchers = query.count()

    # Pagination setup
    page = request.args.get("page", 1, type=int)
    per_page = 25
    vouchers = query.order_by(DisbursementVoucher.date_received.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Item numbers for pagination (first and last on the current page)
    first_item = (vouchers.page - 1) * vouchers.per_page + 1
    last_item = min(vouchers.page * vouchers.per_page, vouchers.total)

    template = "fragments/list_content.html" if request.headers.get("HX-Request") else "pages/list.html"

    # Get filter options for the panel
    categories = Category.query.order_by(Category.name).all()
    resp_centers = ResponsibilityCenter.query.order_by(ResponsibilityCenter.name).all()

    return render_template(
        template,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        first_item=first_item,
        last_item=last_item,
        categories=categories,
        resp_centers=resp_centers,
        filters={
            "category": category_id,
            "resp_center": resp_center_id,
            "mode_of_payment": mode_of_payment,
            "date_from": date_from,
            "date_to": date_to,
        },
    )


@voucher_bp.route("vouchers/export")
@login_required
def export_vouchers():
    import openpyxl

    # Build base query with same filters as list view
    query = DisbursementVoucher.query

    category_id = request.args.get("category", type=int)
    resp_center_id = request.args.get("resp_center", type=int)
    mode_of_payment = request.args.get("mode_of_payment")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    if category_id:
        query = query.filter(DisbursementVoucher.category_id == category_id)
    if resp_center_id:
        query = query.filter(DisbursementVoucher.resp_center_id == resp_center_id)
    if mode_of_payment:
        query = query.filter(DisbursementVoucher.mode_of_payment == mode_of_payment)
    if date_from:
        query = query.filter(DisbursementVoucher.date_received >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.filter(DisbursementVoucher.date_received <= datetime.fromisoformat(date_to))

    # Check if export is for current page only
    page_only = request.args.get("page_only") == "true"
    if page_only:
        page = request.args.get("page", 1, type=int)
        per_page = 25
        paginated = query.order_by(DisbursementVoucher.date_received.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        vouchers = paginated.items
    else:
        vouchers = query.order_by(DisbursementVoucher.date_received.desc()).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vouchers"

    headers = [
        "DV Number",
        "Payee",
        "Particulars",
        "Amount",
        "Mode of Payment",
        "Category",
        "Responsibility Center",
        "Date Received",
    ]
    ws.append(headers)

    for voucher in vouchers:
        ws.append(
            [
                voucher.dv_number or "",
                voucher.payee or "",
                voucher.particulars or "",
                float(voucher.amount) if voucher.amount is not None else None,
                voucher.mode_of_payment or "",
                voucher.category.name if voucher.category else "",
                voucher.resp_center.name if voucher.resp_center else "",
                voucher.date_received.strftime("%Y-%m-%d %H:%M") if voucher.date_received else "",
            ]
        )

    # Auto width (simple heuristic)
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 12), 40)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"vouchers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
    from app.models.voucher import Category, ResponsibilityCenter

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

    # Get filter options for the panel
    categories = Category.query.order_by(Category.name).all()
    resp_centers = ResponsibilityCenter.query.order_by(ResponsibilityCenter.name).all()

    template = "pages/list.html"
    return render_template(
        template,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        first_item=first_item,
        last_item=last_item,
        form=form,
        show_card=True,
        categories=categories,
        resp_centers=resp_centers,
        filters={
            "category": None,
            "resp_center": None,
            "mode_of_payment": None,
            "date_from": None,
            "date_to": None,
        },
    )

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
