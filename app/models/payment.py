from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Payment(BaseModel):
    """
    Tenant-scoped payment record.
    """

    tenant_id = Column(
        Integer,
        ForeignKey("tenant.id"),
        nullable=False,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("order.id"),
        nullable=False
    )

    provider = Column(String(50), nullable=False)  # stripe, paystack, flutterwave

    reference = Column(
        String(255),
        unique=True,
        nullable=False
    )

    amount = Column(Numeric(10, 2), nullable=False)

    status = Column(
        String(50),
        nullable=False
    )  # initiated, success, failed

    order = relationship("Order", back_populates="payment")
