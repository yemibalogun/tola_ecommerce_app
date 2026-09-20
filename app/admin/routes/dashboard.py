# app/admin/routes/dashboard.py

from flask import  render_template
from flask_login import login_required
from app.admin.decorators import admin_required
from app.admin import admin_bp

from flask import render_template, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from typing import Any, Dict, List

from app.extensions.db import db
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.product_variant import ProductVariant
from app.models.tenant import DEFAULT_ACCENT
from app.models.tenant_banner import TenantBanner



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

        total_banners: int = TenantBanner.query.filter_by(
            tenant_id=tenant_id
        ).count()

        metrics: Dict[str, Any] = {
            "total_banners": total_banners,
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
            "total_banners": 0,
            "total_products": 0,
            "total_categories": 0,
            "total_orders": 0,
            "revenue": 0.0,
            "recent_orders": [],
            "low_stock_variants": [],
        }

    tenant = current_user.tenant

    # Onboarding checklist shown until every step is done
    branded: bool = bool(
        tenant.logo
        or tenant.hero_title
        or tenant.tagline
        or (tenant.accent_color or DEFAULT_ACCENT).lower() != DEFAULT_ACCENT
    )
    checklist: List[Dict[str, Any]] = [
        {"label": "Create a category", "hint": "Group products so shoppers can browse", "done": metrics["total_categories"] > 0, "url": url_for("admin_categories.create_category")},
        {"label": "Add your first product", "hint": "Name, price and a great photo", "done": metrics["total_products"] > 0, "url": url_for("admin_products.create_product")},
        {"label": "Make the store yours", "hint": "Logo, accent colour and headline", "done": branded, "url": url_for("tenant_content.store_settings")},
        {"label": "Share your store link", "hint": "Post it on WhatsApp, Instagram, anywhere", "done": metrics["total_orders"] > 0, "url": url_for("store.home", store_slug=tenant.slug)},
    ]

    return render_template(
        "admin/dashboard.html",
        tenant=tenant,
        checklist=checklist,
        **metrics
    )
