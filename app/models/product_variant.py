from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Numeric, ForeignKey
from app.models.base import BaseModel


class ProductVariant(BaseModel):
    """
    Variants allow multiple SKUs per product.
    """

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sku: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    price_override: Mapped[Numeric | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    # 🔹 Pylance now understands this is an int
    stock_quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    product = relationship("Product", back_populates="variants")
