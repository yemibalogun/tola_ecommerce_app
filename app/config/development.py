from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_db"
    )