from datetime import datetime
from app.extensions.db import db
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

class BaseModel(db.Model):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    # Common timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Don't define __init__ - let SQLAlchemy handle it!
    # OR if you need custom logic:
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)