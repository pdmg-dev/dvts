import os
from datetime import datetime
from io import BytesIO

from flask import current_app, render_template, request, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.voucher import Attachment, DisbursementVoucher

from . import voucher_bp
from .forms import DVForm


@voucher_bp.route("vouchers/")
@login_required
def all_vouchers():  # noqa C901
    from app.models.voucher import Category, ResponsibilityCenter

    # Build base query
    query = DisbursementVoucher.query

    # Apply filters (prefer request args; fallback to user preferences when empty)
    args_present = len(request.args) > 0
    prefs = current_user.get_preferences() if hasattr(current_user, "get_preferences") else {}
    voucher_prefs = prefs.get("voucher_list", {}) if not args_present else {}

    category_id = request.args.get("category", type=int) if args_present else voucher_prefs.get("category")
    resp_center_id = request.args.get("resp_center", type=int) if args_present else voucher_prefs.get("resp_center")
    date_from = request.args.get("date_from") if args_present else voucher_prefs.get("date_from")
    date_to = request.args.get("date_to") if args_present else voucher_prefs.get("date_to")
    payee = request.args.get("payee") if args_present else voucher_prefs.get("payee")
    amount_min = request.args.get("amount_min", type=float) if args_present else voucher_prefs.get("amount_min")
    amount_max = request.args.get("amount_max", type=float) if args_present else voucher_prefs.get("amount_max")
    created_from = request.args.get("created_from") if args_present else voucher_prefs.get("created_from")
    created_to = request.args.get("created_to") if args_present else voucher_prefs.get("created_to")
    modified_from = request.args.get("modified_from") if args_present else voucher_prefs.get("modified_from")
    modified_to = request.args.get("modified_to") if args_present else voucher_prefs.get("modified_to")

    if category_id:
        query = query.filter(DisbursementVoucher.category_id == category_id)
    if resp_center_id:
        query = query.filter(DisbursementVoucher.resp_center_id == resp_center_id)
    if date_from:
        try:
            query = query.filter(DisbursementVoucher.date_received >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(DisbursementVoucher.date_received <= datetime.fromisoformat(date_to))
        except ValueError:
            pass
    if payee:
        query = query.filter(DisbursementVoucher.payee.ilike(f"%{payee}%"))
    if amount_min is not None:
        query = query.filter(DisbursementVoucher.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(DisbursementVoucher.amount <= amount_max)
    if created_from:
        try:
            query = query.filter(DisbursementVoucher.created_at >= datetime.fromisoformat(created_from))
        except ValueError:
            pass
    if created_to:
        try:
            query = query.filter(DisbursementVoucher.created_at <= datetime.fromisoformat(created_to))
        except ValueError:
            pass
    if modified_from:
        try:
            query = query.filter(DisbursementVoucher.updated_at >= datetime.fromisoformat(modified_from))
        except ValueError:
            pass
    if modified_to:
        try:
            query = query.filter(DisbursementVoucher.updated_at <= datetime.fromisoformat(modified_to))
        except ValueError:
            pass

    total_vouchers = query.count()

    # Sorting setup
    sort_by = request.args.get("sort_by") if args_present else voucher_prefs.get("sort_by")
    sort_by = sort_by or "date_received"
    sort_dir = request.args.get("sort_dir") if args_present else voucher_prefs.get("sort_dir")
    sort_dir = sort_dir or "desc"

    sort_mapping = {
        "payee": DisbursementVoucher.payee,
        "particulars": DisbursementVoucher.particulars,
        "amount": DisbursementVoucher.amount,
        "date_received": DisbursementVoucher.date_received,
        "created_at": DisbursementVoucher.created_at,
        "updated_at": DisbursementVoucher.updated_at,
        "category": DisbursementVoucher.category_id,
        "resp_center": DisbursementVoucher.resp_center_id,
    }

    sort_column = sort_mapping.get(sort_by, DisbursementVoucher.date_received)
    if sort_dir == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination setup
    page = request.args.get("page", type=int) if args_present else voucher_prefs.get("page")
    page = page or 1
    per_page = 25
    vouchers = query.paginate(page=page, per_page=per_page, error_out=False)

    # Item numbers for pagination (first and last on the current page)
    first_item = (vouchers.page - 1) * vouchers.per_page + 1
    last_item = min(vouchers.page * vouchers.per_page, vouchers.total)

    template = "fragments/list_content.html" if request.headers.get("HX-Request") else "pages/list.html"

    # Get filter options for the panel
    categories = Category.query.order_by(Category.name).all()
    resp_centers = ResponsibilityCenter.query.order_by(ResponsibilityCenter.name).all()

    filters_dict = {
        "category": category_id,
        "resp_center": resp_center_id,
        "date_from": date_from,
        "date_to": date_to,
        "payee": payee,
        "amount_min": amount_min,
        "amount_max": amount_max,
        "created_from": created_from,
        "created_to": created_to,
        "modified_from": modified_from,
        "modified_to": modified_to,
    }

    # Check if user wants to remember their view
    remember_view = request.args.get("remember_view", "true") == "true"

    # Persist preferences server-side when args are present and user wants to remember
    if args_present and remember_view:
        try:
            prefs["voucher_list"] = {
                **filters_dict,
                "sort_by": sort_by,
                "sort_dir": sort_dir,
                "page": page,
            }
            prefs["remember_view"] = True
            current_user.set_preferences(prefs)
            db.session.add(current_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
    elif args_present and not remember_view:
        # Clear saved preferences if user unchecked the box
        try:
            if "voucher_list" in prefs:
                del prefs["voucher_list"]
            prefs["remember_view"] = False
            current_user.set_preferences(prefs)
            db.session.add(current_user)
            db.session.commit()
        except Exception:
            db.session.rollback()

    return render_template(
        template,
        vouchers=vouchers,
        total_vouchers=total_vouchers,
        first_item=first_item,
        last_item=last_item,
        categories=categories,
        resp_centers=resp_centers,
        sort_by=sort_by,
        sort_dir=sort_dir,
        filters=filters_dict,
        remember_view=prefs.get("remember_view", True),
    )


@voucher_bp.route("vouchers/export")
@login_required
def export_vouchers():  # noqa C901
    import openpyxl

    # Build base query with same filters as list view
    query = DisbursementVoucher.query

    category_id = request.args.get("category", type=int)
    resp_center_id = request.args.get("resp_center", type=int)
    mode_of_payment = request.args.get("mode_of_payment")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    payee = request.args.get("payee")
    amount_min = request.args.get("amount_min", type=float)
    amount_max = request.args.get("amount_max", type=float)
    created_from = request.args.get("created_from")
    created_to = request.args.get("created_to")
    modified_from = request.args.get("modified_from")
    modified_to = request.args.get("modified_to")

    if category_id:
        query = query.filter(DisbursementVoucher.category_id == category_id)
    if resp_center_id:
        query = query.filter(DisbursementVoucher.resp_center_id == resp_center_id)
    if mode_of_payment:
        query = query.filter(DisbursementVoucher.mode_of_payment == mode_of_payment)
    if date_from:
        try:
            query = query.filter(DisbursementVoucher.date_received >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(DisbursementVoucher.date_received <= datetime.fromisoformat(date_to))
        except ValueError:
            pass
    if payee:
        query = query.filter(DisbursementVoucher.payee.ilike(f"%{payee}%"))
    if amount_min is not None:
        query = query.filter(DisbursementVoucher.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(DisbursementVoucher.amount <= amount_max)
    if created_from:
        try:
            query = query.filter(DisbursementVoucher.created_at >= datetime.fromisoformat(created_from))
        except ValueError:
            pass
    if created_to:
        try:
            query = query.filter(DisbursementVoucher.created_at <= datetime.fromisoformat(created_to))
        except ValueError:
            pass
    if modified_from:
        try:
            query = query.filter(DisbursementVoucher.updated_at >= datetime.fromisoformat(modified_from))
        except ValueError:
            pass
    if modified_to:
        try:
            query = query.filter(DisbursementVoucher.updated_at <= datetime.fromisoformat(modified_to))
        except ValueError:
            pass

    # Sorting setup
    sort_by = request.args.get("sort_by", "date_received")
    sort_dir = request.args.get("sort_dir", "desc")

    sort_mapping = {
        "payee": DisbursementVoucher.payee,
        "particulars": DisbursementVoucher.particulars,
        "amount": DisbursementVoucher.amount,
        "date_received": DisbursementVoucher.date_received,
        "created_at": DisbursementVoucher.created_at,
        "updated_at": DisbursementVoucher.updated_at,
        "category": DisbursementVoucher.category_id,
        "resp_center": DisbursementVoucher.resp_center_id,
    }

    sort_column = sort_mapping.get(sort_by, DisbursementVoucher.date_received)
    if sort_dir == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Check if export is for current page only
    page_only = request.args.get("page_only") == "true"
    if page_only:
        page = request.args.get("page", 1, type=int)
        per_page = 25
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        vouchers = paginated.items
    else:
        vouchers = query.all()

    # Get custom fields if provided
    custom_fields = request.args.get("fields")
    if custom_fields:
        selected_fields = custom_fields.split(",")
    else:
        # Default fields
        selected_fields = [
            "dv_number",
            "payee",
            "particulars",
            "amount",
            "mode_of_payment",
            "category",
            "resp_center",
            "date_received",
        ]

    # Field mapping: internal name -> (header label, value getter function)
    field_config = {
        "dv_number": ("DV Number", lambda v: v.dv_number or ""),
        "category": ("Category", lambda v: v.category.name if v.category else ""),
        "resp_center": ("Responsibility Center", lambda v: v.resp_center.name if v.resp_center else ""),
        "payee": ("Payee", lambda v: v.payee or ""),
        "particulars": ("Particulars", lambda v: v.particulars or ""),
        "amount": ("Amount", lambda v: float(v.amount) if v.amount is not None else None),
        "mode_of_payment": ("Mode of Payment", lambda v: v.mode_of_payment or ""),
        "date_received": (
            "Date Received",
            lambda v: v.date_received.strftime("%Y-%m-%d %H:%M") if v.date_received else "",
        ),
        "created_at": (
            "Created At",
            lambda v: v.created_at.strftime("%Y-%m-%d %H:%M") if v.created_at else "",
        ),
        "updated_at": (
            "Updated At",
            lambda v: v.updated_at.strftime("%Y-%m-%d %H:%M") if v.updated_at else "",
        ),
    }

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vouchers"

    # Build headers based on selected fields
    headers = [field_config[field][0] for field in selected_fields if field in field_config]
    ws.append(headers)

    # Build rows based on selected fields
    for voucher in vouchers:
        row = [field_config[field][1](voucher) for field in selected_fields if field in field_config]
        ws.append(row)

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
def view_voucher(voucher_id):  # noqa C901

    voucher = DisbursementVoucher.query.get_or_404(voucher_id)

    # Build query with same filters and sorting as the list view
    query = DisbursementVoucher.query

    # Apply filters (prefer request args; fallback to user voucher preferences)
    args_present = len(request.args) > 0
    prefs = current_user.get_preferences() if hasattr(current_user, "get_preferences") else {}
    voucher_prefs = prefs.get("voucher_list", {}) if not args_present else {}

    category_id = request.args.get("category", type=int) if args_present else voucher_prefs.get("category")
    resp_center_id = request.args.get("resp_center", type=int) if args_present else voucher_prefs.get("resp_center")
    date_from = request.args.get("date_from") if args_present else voucher_prefs.get("date_from")
    date_to = request.args.get("date_to") if args_present else voucher_prefs.get("date_to")
    payee = request.args.get("payee") if args_present else voucher_prefs.get("payee")
    amount_min = request.args.get("amount_min", type=float) if args_present else voucher_prefs.get("amount_min")
    amount_max = request.args.get("amount_max", type=float) if args_present else voucher_prefs.get("amount_max")
    created_from = request.args.get("created_from") if args_present else voucher_prefs.get("created_from")
    created_to = request.args.get("created_to") if args_present else voucher_prefs.get("created_to")
    modified_from = request.args.get("modified_from") if args_present else voucher_prefs.get("modified_from")
    modified_to = request.args.get("modified_to") if args_present else voucher_prefs.get("modified_to")

    if category_id:
        query = query.filter(DisbursementVoucher.category_id == category_id)
    if resp_center_id:
        query = query.filter(DisbursementVoucher.resp_center_id == resp_center_id)
    if date_from:
        try:
            query = query.filter(DisbursementVoucher.date_received >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(DisbursementVoucher.date_received <= datetime.fromisoformat(date_to))
        except ValueError:
            pass
    if payee:
        query = query.filter(DisbursementVoucher.payee.ilike(f"%{payee}%"))
    if amount_min is not None:
        query = query.filter(DisbursementVoucher.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(DisbursementVoucher.amount <= amount_max)
    if created_from:
        try:
            query = query.filter(DisbursementVoucher.created_at >= datetime.fromisoformat(created_from))
        except ValueError:
            pass
    if created_to:
        try:
            query = query.filter(DisbursementVoucher.created_at <= datetime.fromisoformat(created_to))
        except ValueError:
            pass
    if modified_from:
        try:
            query = query.filter(DisbursementVoucher.updated_at >= datetime.fromisoformat(modified_from))
        except ValueError:
            pass
    if modified_to:
        try:
            query = query.filter(DisbursementVoucher.updated_at <= datetime.fromisoformat(modified_to))
        except ValueError:
            pass

    total_vouchers = query.count()

    # Preserve originating page for back navigation
    page = request.args.get("page", 1, type=int)

    # Apply sorting (same as all_vouchers route)
    sort_by = request.args.get("sort_by") if args_present else voucher_prefs.get("sort_by")
    sort_by = sort_by or "date_received"
    sort_dir = request.args.get("sort_dir") if args_present else voucher_prefs.get("sort_dir")
    sort_dir = sort_dir or "desc"

    sort_mapping = {
        "payee": DisbursementVoucher.payee,
        "particulars": DisbursementVoucher.particulars,
        "amount": DisbursementVoucher.amount,
        "date_received": DisbursementVoucher.date_received,
        "created_at": DisbursementVoucher.created_at,
        "updated_at": DisbursementVoucher.updated_at,
        "category": DisbursementVoucher.category_id,
        "resp_center": DisbursementVoucher.resp_center_id,
    }

    sort_column = sort_mapping.get(sort_by, DisbursementVoucher.date_received)
    if sort_dir == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Get all filtered/sorted vouchers
    sorted_vouchers = query.all()

    # Find current voucher position in the sorted list
    current_voucher = None
    prev_voucher = None
    next_voucher = None

    for idx, v in enumerate(sorted_vouchers, 1):
        if v.id == voucher_id:
            current_voucher = idx
            prev_voucher = sorted_vouchers[idx - 2] if idx > 1 else None
            next_voucher = sorted_vouchers[idx] if idx < len(sorted_vouchers) else None
            break

    if request.headers.get("HX-Request"):
        layout = request.headers.get("HX-Layout")
        skip_oob = request.headers.get("X-Skip-OOB-Swap") == "true"

        if layout == "split":
            # Return a fragment that includes both the split-pane detail
            # and the detail side-panel (OOB) so HTMX updates both areas.
            template = "fragments/split_detail_content.html"
        elif skip_oob:
            # When filter panel is open and user clicks a row, return only detail
            # content without the OOB side panel swap
            template = "fragments/detail_content_no_oob.html"
        else:
            template = "fragments/detail_content.html"
    else:
        template = "pages/detail.html"

    return render_template(
        template,
        voucher=voucher,
        total_vouchers=total_vouchers,
        current_voucher=current_voucher,
        next_voucher=next_voucher,
        prev_voucher=prev_voucher,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        filters={
            "category": category_id,
            "resp_center": resp_center_id,
            "date_from": date_from,
            "date_to": date_to,
            "payee": payee,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "created_from": created_from,
            "created_to": created_to,
            "modified_from": modified_from,
            "modified_to": modified_to,
        },
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
        sort_by="date_received",
        sort_dir="desc",
        filters={
            "category": None,
            "resp_center": None,
            "date_from": None,
            "date_to": None,
            "payee": None,
            "amount_min": None,
            "amount_max": None,
            "created_from": None,
            "created_to": None,
            "modified_from": None,
            "modified_to": None,
        },
        remember_view=True,
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

    attach = Attachment(voucher_id=voucher_id, filename=filename, filepath=filepath)
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
