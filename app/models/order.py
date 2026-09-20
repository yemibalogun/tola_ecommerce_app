from sqlalchemy import String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel
from decimal import Decimal


class Order(BaseModel):
    """
    Represents a completed or pending checkout.

    Orders can be placed by a signed-in user or by a guest shopper, so
    ``user_id`` is optional and the customer's details are captured inline.
    """
    status: Mapped[str] = mapped_column(String(50))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"))

    # Guest checkout details (also filled for signed-in shoppers)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    @property
    def customer_label(self) -> str:
        """Best available name for the buyer, for admin screens."""
        if self.customer_name:
            return self.customer_name
        if self.user is not None:
            return self.user.email
        return "Guest"

    def __repr__(self) -> str:
        return f"<Order #{self.id} {self.status} {self.total_amount}>"
