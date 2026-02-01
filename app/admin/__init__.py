from flask import Blueprint

# Single source of truth for the admin blueprint
admin_bp: Blueprint = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)

# Import route modules so their view functions get registered
# NOTE: imports are at the bottom to avoid circular imports
from app.admin.routes import products  # noqa: E402

__all__: list[str] = ["admin_bp"]
