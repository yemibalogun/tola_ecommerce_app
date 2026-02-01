from decimal import Decimal
from sqlalchemy import (
    Numeric,
    String,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel
from app.extensions.db import db


class Product(BaseModel):
    __tablename__ = "product"

    """
    Core sellable item.
    """
    id: Mapped[int] = mapped_column(primary_key=True)

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
   
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True)
    
    tenant = relationship("Tenant", back_populates="products")
    category = relationship("Category", back_populates="products")

    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Product {self.name} ({self.slug})>"

