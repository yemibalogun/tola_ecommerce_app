import os
from app.config.base import BaseConfig

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI: str | None = os.environ.get("DATABASE_URL")
