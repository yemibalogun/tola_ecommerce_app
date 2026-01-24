from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel


class Category(BaseModel):
    name = Column(String(120), nullable=False)
    slug = Column(String(120), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")
