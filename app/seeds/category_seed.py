# app/seeds/category_seed.py

from app.models.category import Category
from app.extensions.db import db
from flask_login import current_user
from slugify import slugify
from app.models.category import Category
from app.extensions.db import db
from app.models.tenant import Tenant

CATEGORY_NAMES = [
    # Electronics & Gadgets
    "Smartphones", "Laptops & Computers", "Tablets & Accessories",
    "Wearable Tech", "Audio & Headphones", "Cameras & Photography",
    # Home & Lifestyle
    "Home Appliances", "Kitchen Tools & Gadgets", "Furniture & Decor",
    "Bedding & Linen", "Smart Home Devices", "Gardening & Outdoor",
    # Fashion & Personal Care
    "Men’s Clothing", "Women’s Clothing", "Footwear", "Accessories & Jewelry",
    "Health & Beauty", "Personal Care Devices",
    # Sports & Hobbies
    "Sports Equipment", "Fitness & Wellness", "Outdoor Adventure Gear",
    "Toys & Games", "Musical Instruments", "Arts & Crafts",
    # Digital & Online Products
    "eBooks & Audiobooks", "Online Courses", "Software & Tools",
    "Digital Templates & Themes", "Stock Photos & Graphics", "Music & Audio Files"
]



def seed_categories(tenant_id: int):
    """
    Seed default categories for a tenant.
    """
    existing = Category.query.filter_by(tenant_id=tenant_id).all()
    existing_names = {c.name for c in existing}

    for name in CATEGORY_NAMES:
        if name not in existing_names:
            category = Category()
            category.name=name
            category.slug=slugify(name)
            category.tenant_id=tenant_id
            
            db.session.add(category)
    db.session.commit()
    print(f"Seeded {len(CATEGORY_NAMES)} categories for tenant {tenant_id}.")
