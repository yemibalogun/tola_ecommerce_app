from flask import Blueprint

# Single source of truth for the admin blueprint
admin_bp: Blueprint = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)

product_bp = Blueprint("admin_products", 
                       __name__, 
                       url_prefix="/admin/products"
                    )


# Import route modules so their view functions get registered
# NOTE: imports are at the bottom to avoid circular imports
from app.admin.routes import *

