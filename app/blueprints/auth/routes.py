# app/blueprints/auth/routes.py
from datetime import timedelta

from flask import redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from sqlalchemy import or_

from app.models.user import User

from . import auth_bp
from .forms import LoginForm


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter(
                or_(User.username == form.identifier.data, User.email == form.identifier.data)
            ).first()

            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data, duration=timedelta(days=1))

                """
                if request.headers.get("HX-Request"):
                    response = make_response("", 204)
                    response.headers["HX-Redirect"] = url_for("tracker.view_vouchers")
                    return response """

            if not user:
                form.identifier.errors.append("Couldn't find that email or username")
            elif not user.check_password(form.password.data):
                form.password.errors.append("Incorrect password. Please try again.")
            else:
                login_user(user, remember=form.remember.data, duration=timedelta(days=1))
                return render_template("auth/login_form.html", form=form, success=True)

        return render_template("auth/login_form.html", form=form)
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
