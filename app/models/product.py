from decimal import Decimal
from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Product(BaseModel):
    """
    Core sellable item.
    """

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)

    price = Column(Numeric(10, 2), nullable=False)
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
