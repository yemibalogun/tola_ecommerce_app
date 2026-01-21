from flask import Flask
from flask_migrate import Migrate
from app.extensions.db import db
from app.extensions.cache import cache
from sqlalchemy import create_engine, text
import re, os

migrate = Migrate()


def create_database_if_not_exists(database_uri: str) -> None:
    """
    Creates the database if it does not exist.
    Works only for PostgreSQL.
    """
    # Extract credentials and DB name from URI
    match = re.match(r"postgresql(?:\+psycopg2)?://(.+@.+:\d+)/(.+)", database_uri)
    if not match:
        raise ValueError(f"Invalid database URI: {database_uri}")
    creds, db_name = match.groups()
    default_uri = f"postgresql://{creds}/postgres"  # Connect to default DB

    engine = create_engine(default_uri, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname=:dbname"), {"dbname": db_name}
        ).scalar()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' created automatically.")


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    # ---- Core Flask config ----
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    # Use environment variable for SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] =False
    
    # Runtime validation
    if config_name == "production" and not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("DATABASE_URL must be set in production")

    # Init extensions
    db.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

    if config_name in ("development", "testing"):
        with app.app_context():
            db.create_all()  # now all foreign keys are resolvable

    # Register blueprints
    from app.web import web_bp
    from app.api import api_bp
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
