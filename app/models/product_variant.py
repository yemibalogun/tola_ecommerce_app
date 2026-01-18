from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.models.base import BaseModel


class ProductVariant(BaseModel):
    """
    Variants allow multiple SKUs per product.
    Classical SQLAlchemy style avoids Pylance assignment errors.
    """

    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    tenant_id = Column(Integer, nullable=False)  # 🔹 ADD THIS
    name = Column(String(120), nullable=False)
    sku = Column(String(120), unique=True, nullable=False)
    price_override = Column(Numeric(10, 2), nullable=True)
    stock_quantity = Column(Integer, default=0, nullable=False)

    # Relationship to Product
    product = relationship("Product", back_populates="variants")
