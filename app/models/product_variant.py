from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, Numeric
from .base import BaseModel
from decimal import Decimal
from app.extensions.db import db


class ProductVariant(BaseModel):
    """
    Variants allow multiple SKUs per product.
    Classical SQLAlchemy style avoids Pylance assignment errors.
    """

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenant.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sku: Mapped[str] = mapped_column(String(120), nullable=False)

    price_override: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship to Product
    product = relationship("Product", back_populates="variants")
    
    __table_args__ = (
        db.UniqueConstraint("tenant_id", "sku", name="uq_variant_tenant_sku"),
    )
