import os
import uuid
from typing import Optional
from flask import current_app
from werkzeug.utils import secure_filename


def generate_slug(title: str) -> str:
    """
    Generate a URL-safe slug from a blog title.
    """
    if not title:
        raise ValueError("Title is required for slug generation")

    return (
        title.lower()
        .strip()
        .replace(" ", "-")
        .replace("/", "")
    )


def save_blog_image(file) -> Optional[str]:
    """
    Save uploaded blog image to static/uploads/blogs
    Returns relative path for DB storage.
    """
    if file is None or not file.filename:
        return None
    
    # Flask tying marks this as Optional[str], so we must guard
    static_folder = current_app.static_folder
    if static_folder is None:
        raise RuntimeError("Flask static_folder is not configured")
    
    filename = secure_filename(file.filename)

    # Extra guard (secure_filename may return eempty string)
    if not filename:
        return None

    ext = filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(
        static_folder,      # now guaranteed to be str
        "uploads",
        "blogs"
    )

    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_name)
    file.save(file_path)

    # Store relative path for url_for('static', filename=...)
    return f"uploads/blogs/{unique_name}"
