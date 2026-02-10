# app/models/base.py
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions.db import db

class PKMixin:
    """Provides integer primary key."""
    id: Mapped[int] = mapped_column(primary_key=True)

class TimestampMixin:
    """Provides timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),  # default on insert
        onupdate=lambda: datetime.now(timezone.utc)  # auto-update on update
    )
class BaseModel(PKMixin, TimestampMixin, db.Model):
    __abstract__ = True
    