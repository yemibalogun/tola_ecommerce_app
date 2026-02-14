from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel
from typing import TYPE_CHECKING

# Only imported for type checking (NOT runtime)
if TYPE_CHECKING:
    from .tenant import Tenant

class TenantBanner(BaseModel):
    __tablename__ = "tenant_banner"

    """
    Represents a customizable hero/banner for a tenant's homepage.
    Supports dynamic content, styling, and CTA links.
    """

    # Relationship to tenant
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenant.id", ondelete="CASCADE"),  
        nullable=False,
        index=True,
    )

    
    # Optional full background image (hero-style background)
    background_image: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True             # Optional — banner may use bg_color instead
    )

    # Image hover animation style (zoom, lift, rotate, fade)
    hover_effect: Mapped[str] = mapped_column(
        String(50),
        default="zoom",           # Sensible default
        nullable=False
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="banners",
    )
    # Banner content
    title: Mapped[str] = mapped_column(String(255), nullable=False)  # Main headline
    subtitle: Mapped[str] = mapped_column(String(255), nullable=True)  # Optional subheadline
    image_file: Mapped[str | None] = mapped_column(String(255), nullable=False)  # Banner image

    # Call-to-action (CTA)
    cta_text: Mapped[str] = mapped_column(String(50), nullable=True)  # Button text
    cta_url: Mapped[str] = mapped_column(String(255), nullable=True)  # Link for button

    # Styling / hover effects
    bg_color: Mapped[str] = mapped_column(String(20), nullable=True, default="#f5f5f5")  # Background color
    text_color: Mapped[str] = mapped_column(String(20), nullable=True, default="#000000")  # Text color
    
    # Display order
    order: Mapped[int] = mapped_column(Integer, default=0)  # Determines banner sequence in swiper
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Toggle banner visibility

    def __repr__(self) -> str:
        return f"<TenantBanner {self.title} ({self.tenant_id}) order={self.order}>"
