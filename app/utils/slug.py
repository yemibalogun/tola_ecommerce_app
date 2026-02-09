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


def generate_slug(title: str) -> str:
    """
    Generate a URL-safe slug from a title.

    - Lowercases text
    - Removes non-alphanumeric characters
    - Collapses whitespace/dashes
    - Guarantees non-empty output
    """

    if not title or not title.strip():
        raise ValueError("Title is required to generate slug")

    # Convert to lowercase
    slug = title.lower().strip()

    # Remove anything that isn't a letter, number, space, or dash
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)

    # Replace whitespace with single dashes
    slug = re.sub(r"\s+", "-", slug)

    # Collapse multiple dashes
    slug = re.sub(r"-{2,}", "-", slug)

    return slug

