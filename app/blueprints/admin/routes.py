# app/blueprints/admin/routes.py
from flask import render_template, request
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models.voucher import Category

from . import admin_bp
from .forms import CategoryForm


@admin_bp.get("/categories")
@login_required
def category_index():
    categories = Category.query.order_by(func.lower(Category.name)).all()
    if request.headers.get("HX-Request"):
        return render_template("categories/partials/content.html", categories=categories)
    return render_template("categories/index.html", categories=categories)


@admin_bp.get("/categories/create")
@login_required
def category_create():
    form = CategoryForm()
    return render_template(
        "categories/fragments/content.html",
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
    return render_template("categories/fragments/content.html", form=form, action="create")


@admin_bp.get("/categories/update/<int:category_id>")
@login_required
def category_update(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    return render_template(
        "categories/fragments/content.html",
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
        "categories/fragments/content.html",
        form=form,
        action="update",
        category_id=category.id,
    )


@admin_bp.get("/categories/delete/<int:category_id>")
@login_required
def category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template(
        "categories/fragments/content.html",
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
