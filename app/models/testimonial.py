from app.extensions.db import db
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

class Testimonial(db.Model):
    __tablename__ = "testimonial"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    rating: Mapped[int] = mapped_column(default=5)  # 1 to 5 stars
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    tenant_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey("tenant.id"),
        nullable=False,
        index=True
    )
