from flask import render_template, request
from flask_login import login_required

from app.extensions import db
from app.models.voucher import Category

from . import admin_bp
from .forms import CategoryForm


@admin_bp.route("/categories")
@login_required
def all_categories():
    categories = Category.query.order_by(Category.name).all()
    template = (
        "category/fragments/list_content.html" if request.headers.get("HX-Request") else "category/pages/list.html"
    )
    return render_template(template, categories=categories)


@admin_bp.route("/categories/create", methods=["GET", "POST"])
@login_required
def create_category():
    form = CategoryForm()

    # Handle HTMX request for the form
    if request.method == "GET" and request.headers.get("HX-Request"):
        return render_template(
            "category/fragments/content.html",
            action="create",
            form=form,
        )

    # Handle form submission
    if request.method == "POST":
        if form.validate_on_submit():
            category = Category(name=form.name.data.strip())
            db.session.add(category)
            db.session.commit()

            categories = Category.query.order_by(Category.name).all()
            return render_template(
                "category/fragments/response.html",
                categories=categories,
                action="create",
                form=form,
            )
        return render_template(
            "category/fragments/content.html",
            action="create",
            form=form,
        )


@admin_bp.route("/categories/update/<int:category_id>", methods=["GET", "POST"])
@login_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)

    # Handle HTMX request for the form
    if request.method == "GET" and request.headers.get("HX-Request"):
        return render_template(
            "category/fragments/content.html",
            action="update",
            form=form,
            category_id=category.id,
        )

    # Handle form submission
    if request.method == "POST":
        if form.validate_on_submit():
            form.populate_obj(category)
            db.session.commit()

            categories = Category.query.order_by(Category.name).all()
            return render_template(
                "category/fragments/response.html",
                categories=categories,
                action="update",
                form=form,
            )
        return render_template(
            "category/fragments/content.html",
            action="update",
            form=form,
            category_id=category.id,
        )


@admin_bp.route("/categories/delete/<int:category_id>", methods=["GET", "POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # Handle HTMX request for the confirmation
    if request.method == "GET" and request.headers.get("HX-Request"):
        return render_template("category/fragments/content.html", action="delete", category=category, form=None)

    # Handle form submission
    if request.method == "POST":
        db.session.delete(category)
        db.session.commit()

        categories = Category.query.order_by(Category.name).all()

        return render_template(
            "category/fragments/response.html",
            action="delete",
            category=category,
            categories=categories,
        )
