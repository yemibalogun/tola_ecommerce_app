# app/admin/routes/dashboard.py

from flask import  render_template
from flask_login import login_required
from app.admin.decorators import admin_required
from app.admin import admin_bp

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard() -> str:
    """
    Admin dashboard landing page.
    Access is restricted to authenticated admin users only.
    """
    return render_template("admin/dashboard.html")
