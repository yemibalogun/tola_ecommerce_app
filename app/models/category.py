from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel


class Category(BaseModel):
    
    name: Mapped[str | None] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Add tenant_id
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="categories")
    products = relationship("Product", back_populates="category")
