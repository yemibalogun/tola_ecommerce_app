from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """
    Customer or admin user.
    """

    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)

    tenant_id = Column(ForeignKey("tenant.id"), nullable=False)

    tenant = relationship("Tenant", back_populates="users")
    orders = relationship("Order", back_populates="user")
