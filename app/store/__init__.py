from flask import Blueprint

# Public storefront for a single tenant. Every store gets a shareable URL:
#   /store/<store_slug>/
store_bp = Blueprint("store", __name__, url_prefix="/store/<store_slug>")

from app.store import routes  # noqa: E402,F401  (registers views)
