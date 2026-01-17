from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Numeric
from decimal import Decimal
from app.extensions.db import db

class OrderItem(db.Model):
    __tablename__ = "order_item"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variant.id"))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
