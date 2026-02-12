# app/admin/routes/orders.py

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions.db import db
from app.models.order import Order
from app.admin.decorators import admin_required
from typing import Optional
from app.admin import orders_bp


@orders_bp.route("/", methods=["GET"])
@login_required
@admin_required
def list_orders():
    """
    List all orders for the current tenant.
    """
    try:
        orders = Order.query.filter_by(
            tenant_id=current_user.tenant_id
        ).order_by(Order.created_at.desc()).all()

        return render_template(
            "admin/orders/list.html",
            orders=orders
        )
    except Exception as e:
        flash("Failed to load orders.", "danger")
        return render_template("admin/orders/list.html", orders=[])


@orders_bp.route("/<int:order_id>", methods=["GET"])
@login_required
@admin_required
def view_order(order_id: int):
    """
    View a single order (tenant-protected).
    """
    order: Optional[Order] = Order.query.filter_by(
        id=order_id,
        tenant_id=current_user.tenant_id
    ).first()

    if not order:
        flash("Order not found.", "warning")
        return redirect(url_for("admin_orders.list_orders"))

    return render_template(
        "admin/orders/detail.html",
        order=order
    )


@orders_bp.route("/<int:order_id>/status", methods=["POST"])
@login_required
@admin_required
def update_order_status(order_id: int):
    """
    Update order status safely.
    """
    order: Optional[Order] = Order.query.filter_by(
        id=order_id,
        tenant_id=current_user.tenant_id
    ).first()

    if not order:
        flash("Order not found.", "warning")
        return redirect(url_for("admin_orders.list_orders"))

    new_status: str = request.form.get("status", "").strip()

    allowed_statuses = ["pending", "paid", "shipped", "completed", "cancelled"]

    if new_status not in allowed_statuses:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin_orders.view_order", order_id=order.id))

    try:
        order.status = new_status
        db.session.commit()
        flash("Order status updated successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to update order.", "danger")

    return redirect(url_for("admin_orders.view_order", order_id=order.id))
