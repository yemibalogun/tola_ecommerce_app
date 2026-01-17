from flask import Blueprint

# define blueprint
web_bp = Blueprint("web", __name__)

# optional: import your routes here so they register automatically
from app.web import routes  # make sure routes.py exists
