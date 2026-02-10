import re
from typing import Any
from app.extensions.db import db
from app.models.blog import Blog
import unicodedata



def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def unique_slug(
    model: type[Any],
    value: str,
    slug_field: str = "slug",
) -> str:
    # Generate a unique slug for any SQLAlchemy model.
    if not value:
        raise ValueError("Slug value must be non-empty")

    base = slugify(value)
    slug = base
    counter = 1

    while db.session.query(model).filter_by(**{slug_field: slug}).first():
        slug = f"{base}-{counter}"
        counter += 1

    return slug


def generate_unique_slug(title: str, tenant_id: int) -> str:
    """Generate a unique slug for a tenant."""
    base_slug = generate_slug(title)
    slug = base_slug
    counter = 1

    # Check for existing slug in the tenant
    while Blog.query.filter_by(tenant_id=tenant_id, slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def generate_slug(title: str) -> str:
    """
    Generate a URL-friendly slug from a title.
    Converts to lowercase, removes non-alphanumeric chars, replaces spaces with '-'.
    """
    # Normalize unicode chars
    title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    # Lowercase
    title = title.lower()
    # Remove non-alphanumeric characters except spaces
    title = re.sub(r"[^a-z0-9\s-]", "", title)
    # Replace spaces and repeated dashes with single dash
    title = re.sub(r"[\s-]+", "-", title).strip("-")
    return title


