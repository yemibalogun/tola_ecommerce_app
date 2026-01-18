# manage.py
from app import create_app
from app.extensions.db import db

app = create_app("development")  # your config name

# Create tables inside app context
with app.app_context():
    db.create_all()
    print("All tables created successfully.")
