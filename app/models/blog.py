from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey
from .base import BaseModel
from app.extensions.db import db


class Blog(BaseModel):
    __tablename__ = "blog"

    id: Mapped[int] = mapped_column(primary_key=True)

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenant.id"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Store image path relative to /static
    image_path: Mapped[Optional[str]] = mapped_column(String(255))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "slug", name="uq_blog_tenant_slug"),
    )
