from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel


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
    products = relationship("Product", back_populates="tenant")
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="tenant")
    categories = relationship(
    "Category",
    back_populates="tenant",
    cascade="all, delete-orphan"
)

