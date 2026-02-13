# app/admin/routes/inventory.py

from flask import redirect, url_for, flash, request, jsonify
from app.extensions.db import db
from app.models.product_variant import ProductVariant
from app.admin.forms import InventoryAdjustForm
from app.services.inventory_service import apply_inventory_delta, get_stock_status
from app.admin import admin_bp
from flask_login import login_required, current_user
from app.admin.decorators import admin_required

@admin_bp.route("/variants/<int:variant_id>/inventory", methods=["POST"])
@login_required
@admin_required
def update_inventory(variant_id: int):
    """
    Inventory update via standard HTML form.
    Used as a fallback when JS is disabled.
    """
    form = InventoryAdjustForm()

    if not form.validate_on_submit():
        flash("Invalid inventory adjustment.", "danger")
        return redirect(request.referrer or url_for("admin.dashboard"))

    variant: ProductVariant | None = ProductVariant.query.get(variant_id)

    if variant is None:
        flash("Variant not found.", "danger")
        return redirect(request.referrer or url_for("admin.dashboard"))

    delta: int = form.delta.data or 0

    if delta == 0:
        flash("Adjustment amount cannot be zero.", "warning")
        return redirect(request.referrer or url_for("admin.dashboard"))

    apply_inventory_delta(variant, delta)

    flash(f"Inventory updated ({delta:+}).", "success")
    return redirect(request.referrer or url_for("admin.dashboard"))


@admin_bp.route("/variants/<int:variant_id>/inventory/ajax", methods=["POST"])
@login_required
@admin_required
def update_inventory_ajax(variant_id: int):
    """Inventory update via AJAX."""
    data: dict | None = request.get_json(silent=True)

    if not data or "delta" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    try:
        delta: int = int(data["delta"])
    except (TypeError, ValueError):
        return jsonify({"error": "Delta must be an integer"}), 400

    if delta == 0:
        return jsonify({"error": "Delta cannot be zero"}), 400

    variant: ProductVariant = ProductVariant.query.get_or_404(variant_id)

    try:
        apply_inventory_delta(variant, delta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "variant_id": variant.id,
        "stock_quantity": variant.stock_quantity,
        "stock_status": get_stock_status(variant.stock_quantity)
    })
