from app import create_app
from app.extensions.db import db
from app.models.user import User
from app.models.tenant import Tenant 
from sqlalchemy.exc import IntegrityError

app = create_app("development")

with app.app_context():
    admin_email = "admin@example.com"
    admin_password = "StrongPassword123"
    tenant_name: str = "Main Tenant"

    try:
        # ---- Ensure tenant exists ---
        tenant: Tenant | None = Tenant.query.filter_by(name=name).first()

        if tenant is None:
            tenant = Tenant(name=tenant_name)
            db.session.add(tenant)
            db.session.flush()
            # flush assigns tenant.id WITHOUT committing yet

        # ---- Ensure admin user exists ---
        existing: User | None = User.query.filter_by(email=admin_email).first()

        if existing:
            print("Admin user already exists.")
        else:
            
            admin = User()
            admin.email=admin_email 
            admin.is_admin=True
            admin.tenant_id=1
        
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created: {admin_email} (tenant_id={tenant.id})")
        
    except IntegrityError as exc:
        db.session.rollback()
        raise RuntimeError("Failed to create admin user") from exc