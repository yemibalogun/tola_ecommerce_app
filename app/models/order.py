from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import BaseModel
from decimal import Decimal 

class Order(BaseModel):
    """
    Represents a completed or pending checkout.
    """

    status: Mapped[str] = mapped_column(String(50))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"))

    user = relationship("User", back_populates="orders")
    tenant = relationship("Tenant", back_populates="orders")
    
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )
