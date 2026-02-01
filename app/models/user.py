from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .base import BaseModel


class User(BaseModel, UserMixin):
    """
    Customer or admin user.
    """
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    orders = relationship("Order", back_populates="user")

    # Password helpers
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
