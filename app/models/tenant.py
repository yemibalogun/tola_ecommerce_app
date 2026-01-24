from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel


class Tenant(BaseModel):
    """
    Represents a store / website in a multi-tenant SaaS setup.
    """

    name = Column(String(120), nullable=False)
    slug = Column(String(120), unique=True, nullable=False)

    products = relationship("Product", back_populates="tenant")
    users = relationship("User", back_populates="tenant")
    orders = relationship("Order", back_populates="tenant")
