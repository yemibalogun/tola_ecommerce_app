from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Numeric
from app.extensions.db import db


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)

    # Tenant scoping — REQUIRED for safe multi-tenancy
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenant.id"),
        nullable=False,
        index=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variant.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)

    unit_price = db.Column(
        Numeric(10, 2),
        nullable=False
    )

    order = relationship("Order", back_populates="items")
