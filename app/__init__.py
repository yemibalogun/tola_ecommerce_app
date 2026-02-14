from flask import Flask, request, g
from flask_migrate import Migrate
from app.extensions.db import db
from app.extensions.login import login_manager
from app.extensions.cache import cache
from sqlalchemy import create_engine, text
from flask_wtf import CSRFProtect
import re, os
from datetime import datetime
from app.models import Tenant

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
    # Build absolute paths for templates and static
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)

    @app.context_processor
    def inject_globals() -> dict[str, object]:
        """
        Inject global template variables.
        """
        try:
            current_year: int = datetime.utcnow().year
        except Exception:
            current_year = 2026

        return {
            "current_year": current_year,
            "tenant": getattr(g, "tenant", None),
        }

    # ---- Core Flask config ----
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "uploads", "products"
    )

    # Use environment variable for SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] =False
    
    # Runtime validation
    if config_name == "production" and not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("DATABASE_URL must be set in production")

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    CSRFProtect(app)
    
    if config_name in ("development", "testing"):
        with app.app_context():
            # --- Import all models first ---
            from app.models import base, tenant, user, product, order, category, product_variant, payment, order_item, inventory, testimonial, blog, tenant_banner
            # --- Then create tables ---
            db.create_all()  # now all foreign keys are resolvable

    # Register blueprints
    from app.web import web_bp
    from app.api import api_bp
    from app.admin import auth_bp, product_bp, admin_bp, admin_categories, orders_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(admin_categories)
    app.register_blueprint(orders_bp)

    # -------------------------------
    # 1️⃣ Load tenant before request
    # -------------------------------
    @app.before_request
    def load_current_tenant() -> None:
        """
        Resolve tenant from subdomain.
        Stores tenant globally in flask.g.
        Safe for localhost and production.
        """

        try:
            host: str = request.host.split(":")[0]
            parts: list[str] = host.split(".")

            # Handle localhost (tenant.localhost)
            if "localhost" in host:
                if len(parts) >= 2:
                    subdomain: str = parts[0]
                else:
                    g.tenant = None
                    return
            else:
                # Production domain (tenant.domain.com)
                if len(parts) >= 3:
                    subdomain = parts[0]
                else:
                    g.tenant = None
                    return

            tenant: Tenant | None = (
                db.session.query(Tenant)
                .filter(Tenant.slug == subdomain)
                .first()
            )

            g.tenant = tenant

        except Exception:
            # Fail safe — never break request cycle
            g.tenant = None


    # -------------------------------
    # 2️⃣ Inject tenant into templates
    # -------------------------------
    

     # Create database if it doesn't exist (PostgreSQL only)

    return app
