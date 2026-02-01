from app import create_app
from app.extensions.db import db
from app.models.user import User

app = create_app("development")

with app.app_context():
    admin_email = "admin@example.com"
    admin_password = "StrongPassword123"

    existing = User.query.filter_by(email=admin_email).first()
    if not existing:
        admin = User()
        admin.email=admin_email 
        admin.is_admin=True
        admin.tenant_id=1
    
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {admin_email}")
    else:
        print("Admin user already exists.")
