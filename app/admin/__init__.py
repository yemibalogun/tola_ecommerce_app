from flask import Blueprint

# Single source of truth for the admin blueprint
admin_bp: Blueprint = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)

product_bp = Blueprint(
    "admin_products", 
    __name__, 
    url_prefix="/admin/products"
)

admin_categories = Blueprint(
    "admin_categories",
    __name__,
    url_prefix="/admin/categories",
)

auth_bp = Blueprint(
    "auth", 
    __name__, 
    url_prefix="/admin/auth"
)

orders_bp = Blueprint(
    "admin_orders",
    __name__,
    url_prefix="/admin/orders"
)


# Import route modules so their view functions get registered
# NOTE: imports are at the bottom to avoid circular imports
from app.admin.routes import *

