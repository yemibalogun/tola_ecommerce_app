from flask import redirect, url_for, flash, request
from app.extensions.db import db
from app.models.product_variant import ProductVariant
from app.admin.forms import InventoryAdjustForm
from app.admin import admin_bp


@admin_bp.route("/variants/<int:variant_id>/inventory", methods=["POST"])
def update_inventory(variant_id: int):
    form = InventoryAdjustForm()

    # Defensive: reject invalid form submissions
    if not form.validate_on_submit():
        flash("Invalid inventory adjustment.", "danger")
        return redirect(request.referrer or url_for("admin.dashboard"))

    variant: ProductVariant | None = ProductVariant.query.get(variant_id)

    if variant is None:
        flash("Variant not found.", "danger")
        return redirect(request.referrer or url_for("admin.dashboard"))

    delta: int = form.delta.data or 0

    # Optionally add a check to prevent 0 adjustments
    if delta == 0:
        flash("Adjustment amount cannont be zero.", "danger")
        return redirect(request.referrer or url_for("admin.dashboard"))

    # Prevent negative stock edge case
    new_stock = max(0, variant.stock_quantity + delta)

    variant.stock_quantity = new_stock
    db.session.commit()

    flash(f"Inventory updated ({delta:+}).", "success")
    return redirect(request.referrer)
