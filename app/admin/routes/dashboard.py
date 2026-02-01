# app/admin/routes/dashboard.py

from flask import Blueprint, render_template
from flask_login import login_required
from app.admin.decorators import admin_required

# This must be named admin_bp
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard() -> str:
    """
    Admin dashboard landing page.
    Access is restricted to authenticated admin users only.
    """
    return render_template("admin/dashboard.html")
