from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.extensions.db import db

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
