from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel
from app.extensions.db import db


class Category(BaseModel):

    name: Mapped[str | None] = mapped_column(String(255), nullable=False)
    # Unique per store, so two stores can both have a "Headphones" category
    slug: Mapped[str] = mapped_column(String(255), nullable=False)

    # Add tenant_id
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="categories")
    products = relationship("Product", back_populates="category")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "slug", name="uq_category_tenant_slug"),
    )
