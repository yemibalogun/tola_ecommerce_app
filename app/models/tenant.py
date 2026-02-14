from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tenant_banner import TenantBanner

class Tenant(BaseModel):
    __tablename__ = "tenant"

    """
    Represents a store / website in a multi-tenant SaaS setup.
    """
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    slug: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False
    )

    # Light/Dark hero theme per tenant
    hero_theme: Mapped[str] = mapped_column(
        String(20),
        default="light",          # Default theme
        nullable=False            # Always enforce a theme value
    )

    # Use string name instead of importing the model
    banners: Mapped[list["TenantBanner"]] = relationship(
        "TenantBanner",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    products = relationship("Product", back_populates="tenant")
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="tenant")
    categories = relationship(
    "Category",
    back_populates="tenant",
    cascade="all, delete-orphan"
)

