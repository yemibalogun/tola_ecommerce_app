# app/admin/routes/dashboard.py

from flask import  render_template
from flask_login import login_required
from app.admin.decorators import admin_required
from app.admin import admin_bp

from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from typing import Any, Dict, List

from app.extensions.db import db
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.product_variant import ProductVariant



@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard with tenant-isolated metrics.
    """
    tenant_id: int = current_user.tenant_id

    try:
        # ---- Basic Counts ----
        total_products: int = Product.query.filter_by(
            tenant_id=tenant_id
        ).count()

        total_categories: int = Category.query.filter_by(
            tenant_id=tenant_id
        ).count()

        total_orders: int = Order.query.filter_by(
            tenant_id=tenant_id
        ).count()

        # ---- Revenue (only paid or completed) ----
        revenue: float = (
            db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0))
            .filter(
                Order.tenant_id == tenant_id,
                Order.status.in_(["paid", "completed"])
            )
            .scalar()
        ) or 0.0

        # ---- Recent Orders ----
        recent_orders: List[Order] = (
            Order.query.filter_by(tenant_id=tenant_id)
            .order_by(Order.created_at.desc())
            .limit(5)
            .all()
        )

        # ---- Low Stock Variants (threshold < 5) ----
        low_stock_variants: List[ProductVariant] = (
            ProductVariant.query.filter(
                ProductVariant.tenant_id == tenant_id,
                ProductVariant.stock_quantity < 5
            )
            .order_by(ProductVariant.stock_quantity.asc())
            .limit(5)
            .all()
        )

        metrics: Dict[str, Any] = {
            "total_products": total_products,
            "total_categories": total_categories,
            "total_orders": total_orders,
            "revenue": float(revenue),
            "recent_orders": recent_orders,
            "low_stock_variants": low_stock_variants,
        }

    except Exception:
        # Defensive fallback
        metrics = {
            "total_products": 0,
            "total_categories": 0,
            "total_orders": 0,
            "revenue": 0.0,
            "recent_orders": [],
            "low_stock_variants": [],
        }

    return render_template(
        "admin/dashboard.html",
        **metrics
    )
