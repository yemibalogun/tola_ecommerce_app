from flask import jsonify
from app.api import api_bp

@api_bp.route("/status")
def status():
    return jsonify({"status": "ok"})
