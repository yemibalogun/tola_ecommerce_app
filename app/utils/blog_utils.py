import os
import uuid
from typing import Optional
from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename


# Maximum dimensions for blog images
MAX_WIDTH = 800
MAX_HEIGHT = 450

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
    Save uploaded blog image to static/uploads/blogs and resize it.
    Returns relative path for DB storage.
    """
    if file is None or not file.filename:
        return None

    static_folder = current_app.static_folder
    if not static_folder:
        raise RuntimeError("Flask static_folder is not configured")

    filename = secure_filename(file.filename)
    if not filename:
        return None

    ext = filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(static_folder, "uploads", "blogs")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_name)

    # Save and resize image using Pillow
    image = Image.open(file)
    image.thumbnail((MAX_WIDTH, MAX_HEIGHT))  # maintains aspect ratio
    image.save(file_path)

    return f"uploads/blogs/{unique_name}"
