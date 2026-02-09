# app/admin/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(func):
    """Protect a route so that only authenticated admin users can access it."""
    @wraps(func)  # preserves function metadata
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return wrapper

