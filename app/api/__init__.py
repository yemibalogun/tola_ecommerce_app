from flask import Blueprint

# define blueprint
api_bp = Blueprint("api", __name__)

# optional: import your API endpoints
from app.api import routes  # make sure routes.py exists
