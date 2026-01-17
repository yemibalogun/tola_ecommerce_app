from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Payment(BaseModel):
    """
    Payment record independent of provider.
    """

    order_id = Column(ForeignKey("order.id"), nullable=False)
    provider = Column(String(50))  # stripe, paystack, flutterwave
    reference = Column(String(255), unique=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50))  # initiated, success, failed

    order = relationship("Order", back_populates="payment")
