from app.config.development import DevelopmentConfig
from app.config.production import ProductionConfig

CONFIG_MAP: dict[str, type] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
