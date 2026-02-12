# seed.py

from app import create_app
from app.extensions.db import db
from app.seeds.category_seed import seed_categories

app = create_app("development")

with app.app_context():
    # Replace 1 with the tenant ID you want to seed
    seed_categories(tenant_id=1)
