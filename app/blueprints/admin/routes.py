# app/blueprints/admin/routes.py
from flask import render_template, request
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models.user import Role
from app.models.voucher import Category, ResponsibilityCenter

from . import admin_bp
from .forms import CategoryForm, OfficeForm, RoleForm


# User Management Routes -----------------------------------------------------
@admin_bp.get("/users")
@login_required
def user_index():
    # Placeholder for user index route
    return "User Index Page"


# Roles Management Routes -----------------------------------------------------
@admin_bp.get("/roles")
@login_required
def role_index():
    roles = Role.query.order_by(func.lower(Role.name)).all()
    if request.headers.get("HX-Request"):
        return render_template("roles/fragments/content.html", roles=roles)
    return render_template("roles/index.html", roles=roles)


@admin_bp.get("/roles/create")
@login_required
def role_create():
    form = RoleForm()
    return render_template(
        "roles/fragments/modal_content.html",
        action="create",
        form=form,
    )


@admin_bp.post("/roles/create")
@login_required
def role_create_post():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data.strip())
        db.session.add(role)
        db.session.commit()

        roles = Role.query.order_by(func.lower(Role.name)).all()
        return (
            render_template("roles/fragments/response.html", roles=roles),
            200,
            {"HX-Trigger": "postSuccess"},
        )
    return render_template("roles/fragments/modal_content.html", form=form, action="create")


@admin_bp.get("/roles/update/<int:role_id>")
@login_required
def role_update(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)
    return render_template(
        "roles/fragments/modal_content.html",
        action="update",
        form=form,
        role_id=role.id,
    )


@admin_bp.post("/roles/update/<int:role_id>")
@login_required
def role_update_post(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm()
    if form.validate_on_submit():
        form.populate_obj(role)
        db.session.commit()

        roles = Role.query.order_by(func.lower(Role.name)).all()
        return (
            render_template("roles/fragments/response.html", roles=roles),
            200,
            {"HX-Trigger": "postSuccess"},
        )
    return render_template(
        "roles/fragments/modal_content.html",
        form=form,
        action="update",
        role_id=role.id,
    )


@admin_bp.get("/roles/delete/<int:role_id>")
@login_required
def role_delete(role_id):
    role = Role.query.get_or_404(role_id)
    return render_template(
        "roles/fragments/modal_content.html",
        action="delete",
        role=role,
    )


@admin_bp.post("/roles/delete/<int:role_id>")
@login_required
def role_delete_post(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()

    roles = Role.query.order_by(func.lower(Role.name)).all()
    return (
        render_template("roles/fragments/response.html", roles=roles),
        200,
        {"HX-Trigger": "postSuccess"},
    )


# Category Management Routes -------------------------------------------------
@admin_bp.get("/categories")
@login_required
def category_index():
    categories = Category.query.order_by(func.lower(Category.name)).all()
    if request.headers.get("HX-Request"):
        return render_template("categories/fragments/content.html", categories=categories)
    return render_template("categories/index.html", categories=categories)


@admin_bp.get("/categories/create")
@login_required
def category_create():
    form = CategoryForm()
    return render_template(
        "categories/fragments/modal_content.html",
        action="create",
        form=form,
    )


@admin_bp.post("/categories/create")
@login_required
def category_create_post():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data.strip())
        db.session.add(category)
        db.session.commit()

        categories = Category.query.order_by(func.lower(Category.name)).all()
        return (
            render_template("categories/fragments/response.html", categories=categories),
            200,
            {"HX-Trigger": "postSuccess"},
        )
    return render_template("categories/fragments/modal_content.html", form=form, action="create")


@admin_bp.get("/categories/update/<int:category_id>")
@login_required
def category_update(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    return render_template(
        "categories/fragments/modal_content.html",
        action="update",
        form=form,
        category_id=category.id,
    )


@admin_bp.post("/categories/update/<int:category_id>")
@login_required
def category_update_post(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        form.populate_obj(category)
        db.session.commit()

        categories = Category.query.order_by(func.lower(Category.name)).all()
        return (
            render_template("categories/fragments/response.html", categories=categories),
            200,
            {"HX-Trigger": "postSuccess"},
        )
    return render_template(
        "categories/fragments/modal_content.html",
        form=form,
        action="update",
        category_id=category.id,
    )


@admin_bp.get("/categories/delete/<int:category_id>")
@login_required
def category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template(
        "categories/fragments/modal_content.html",
        action="delete",
        category=category,
    )


@admin_bp.post("/categories/delete/<int:category_id>")
@login_required
def category_delete_post(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

    categories = Category.query.order_by(func.lower(Category.name)).all()
    return (
        render_template("categories/fragments/response.html", categories=categories),
        200,
        {"HX-Trigger": "postSuccess"},
    )


# Office Management Routes -------------------------------------------------
@admin_bp.get("/offices")
@login_required
def office_index():
    offices = ResponsibilityCenter.query.order_by(func.lower(ResponsibilityCenter.name)).all()
    if request.headers.get("HX-Request"):
        return render_template("offices/fragments/content.html", offices=offices)
    return render_template("offices/index.html", offices=offices)


@admin_bp.get("/offices/create")
@login_required
def office_create():
    form = OfficeForm()
    return render_template(
        "offices/fragments/modal_content.html",
        action="create",
        form=form,
    )


@admin_bp.post("/offices/create")
@login_required
def office_create_post():
    form = OfficeForm()
    if form.validate_on_submit():
        office = ResponsibilityCenter(
            name=form.name.data.strip(),
            acronym=form.acronym.data.strip() or None,
            code=form.code.data.strip() or None,
        )
        db.session.add(office)
        db.session.commit()

        offices = ResponsibilityCenter.query.order_by(func.lower(ResponsibilityCenter.name)).all()
        return (
            render_template("offices/fragments/response.html", offices=offices),
            200,
            {"HX-Trigger": "postSuccess"},
        )
    return render_template("offices/fragments/modal_content.html", form=form, action="create")


@admin_bp.get("/offices/update/<int:office_id>")
@login_required
def office_update(office_id):
    office = ResponsibilityCenter.query.get_or_404(office_id)
    form = OfficeForm(obj=office)
    return render_template(
        "offices/fragments/modal_content.html",
        action="update",
        form=form,
        office_id=office.id,
    )


@admin_bp.post("/offices/update/<int:office_id>")
@login_required
def office_update_post(office_id):
    office = ResponsibilityCenter.query.get_or_404(office_id)
    form = OfficeForm()
    if form.validate_on_submit():
        office.name = form.name.data.strip()
        office.acronym = form.acronym.data.strip() or None
        office.code = form.code.data.strip() or None
        db.session.commit()

        offices = ResponsibilityCenter.query.order_by(func.lower(ResponsibilityCenter.name)).all()
        return (
            render_template("offices/fragments/response.html", offices=offices),
            200,
            {"HX-Trigger": "postSuccess"},
        )
    return render_template(
        "offices/fragments/modal_content.html",
        form=form,
        action="update",
        office_id=office.id,
    )


@admin_bp.get("/offices/delete/<int:office_id>")
@login_required
def office_delete(office_id):
    office = ResponsibilityCenter.query.get_or_404(office_id)
    return render_template(
        "offices/fragments/modal_content.html",
        action="delete",
        office=office,
    )


@admin_bp.post("/offices/delete/<int:office_id>")
@login_required
def office_delete_post(office_id):
    office = ResponsibilityCenter.query.get_or_404(office_id)
    db.session.delete(office)
    db.session.commit()

    offices = ResponsibilityCenter.query.order_by(func.lower(ResponsibilityCenter.name)).all()
    return (
        render_template("offices/fragments/response.html", offices=offices),
        200,
        {"HX-Trigger": "postSuccess"},
    )
