from decimal import Decimal
from sqlalchemy import (
    Column,
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
    """
    Core sellable item.
    """
    id: Mapped[int] = mapped_column(primary_key=True)

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)

    is_active = Column(Boolean, default=True)

    tenant_id = Column(ForeignKey("tenant.id"), nullable=False)
    category_id = Column(ForeignKey("category.id"), nullable=True)

    tenant = relationship("Tenant", back_populates="products")
    category = relationship("Category", back_populates="products")
    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )
