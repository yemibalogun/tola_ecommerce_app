# app/admin/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.admin.forms import AdminLoginForm
from app.models.user import User
from werkzeug.security import check_password_hash
from app.admin import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to admin dashboard
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()

    if form.validate_on_submit():
        email_raw = form.email.data
        password_raw = form.password.data

        # Ensure values are not None
        if not email_raw or not password_raw:
            flash("Email and password are required", "danger")
            return render_template("admin/login.html", form=form)

        email: str = email_raw.strip().lower()
        password: str = password_raw

        # Attempt to fetch admin user
        user = User.query.filter_by(email=email, is_admin=True).first()

        if user and user.check_password(password):
            login_user(user, remember=form.remember_me.data)
            flash("Welcome back!", "success")

            # Redirect to 'next' if specified in query params
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))
        
        flash("Invalid email or password", "danger")

    return render_template("admin/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
