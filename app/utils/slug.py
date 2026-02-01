import re
from typing import Any
from app.extensions.db import db


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def unique_slug(
    model: type[Any],
    value: str,
    slug_field: str = "slug",
) -> str:
    # Generate a uniqus slug for any SQLAlchemy model.
    if not value:
        raise ValueError("Slug value must be non-empty")

    base = slugify(value)
    slug = base
    counter = 1

    while db.session.query(model).filter_by(**{slug_field: slug}).first():
        slug = f"{base}-{counter}"
        counter += 1

    return slug
