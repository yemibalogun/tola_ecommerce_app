from flask import Flask
from app.extensions.db import db
from app.extensions.cache import cache

def create_app(config_name: str = "production") -> Flask:
    """
    Flask app factory.

    Args:
        config_name: str - the config class name (production, development, etc.)

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Load config safely
    app.config.from_object(f"app.config.{config_name.capitalize()}Config")

    # Initialize extensions (db, cache)
    db.init_app(app)
    cache.init_app(app)

    # Register blueprints
    from app.web import web_bp
    from app.api import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
