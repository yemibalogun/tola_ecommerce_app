from sqlalchemy import String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tenant_banner import TenantBanner

DEFAULT_ACCENT = "#6d5dfc"


class Tenant(BaseModel):
    __tablename__ = "tenant"

    """
    Represents a store / website in a multi-tenant SaaS setup.
    Everything a store owner can customise from the dashboard lives here.
    """
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    # Public handle used in the shareable store URL: /store/<slug>
    slug: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False
    )

    # Light/Dark hero theme per tenant
    hero_theme: Mapped[str] = mapped_column(
        String(20),
        default="dark",
        nullable=False
    )

    # ---- Branding ----
    tagline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    about: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    accent_color: Mapped[str] = mapped_column(
        String(20),
        default=DEFAULT_ACCENT,
        server_default=DEFAULT_ACCENT,
        nullable=False,
    )
    currency_symbol: Mapped[str] = mapped_column(
        String(8),
        default="₦",
        server_default="₦",
        nullable=False,
    )

    # ---- Homepage hero ----
    # Wrap a word in *asterisks* to render it with the accent gradient.
    hero_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hero_subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hero_image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Contact ----
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

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

    @property
    def display_hero_title(self) -> str:
        return self.hero_title or f"Welcome to *{self.name}*"

    @property
    def display_hero_subtitle(self) -> str:
        return self.hero_subtitle or self.tagline or "Thoughtfully chosen products, delivered with care."

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"
