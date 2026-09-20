import os
import uuid
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app
from typing import Optional


def save_product_image(file: FileStorage) -> str:
    """
    Saves an uploaded product image and returns its relative path.
    """
    # Defensive check
    if not file or not file.filename:
        raise ValueError("Invalid image file")

    # Secure original filename
    filename = secure_filename(file.filename)

    # Extract extension safely
    _, ext = os.path.splitext(filename)

    # Generate collision-safe filename
    new_filename = f"{uuid.uuid4().hex}{ext.lower()}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, new_filename)
    file.save(file_path)

    # Store relative path in DB
    return f"admin/uploads/products/{new_filename}"


def _save_static_upload(file: Optional[FileStorage], folder: str) -> Optional[str]:
    """
    Save an uploaded file to static/uploads/<folder> under a collision-safe
    name. Returns the path relative to /static, or None if nothing was uploaded.
    """
    if file is None or not getattr(file, "filename", None):
        return None

    try:
        _, ext = os.path.splitext(secure_filename(file.filename))
        new_filename: str = f"{uuid.uuid4().hex}{ext.lower()}"

        upload_folder: str = os.path.join(
            current_app.root_path, "static", "uploads", folder
        )
        os.makedirs(upload_folder, exist_ok=True)

        # Save under the same name we store in the DB
        file.save(os.path.join(upload_folder, new_filename))

        return f"uploads/{folder}/{new_filename}"

    except Exception:
        current_app.logger.exception("Failed to save upload to %s", folder)
        return None


def save_banner_image(file: Optional[FileStorage]) -> Optional[str]:
    """
    Save uploaded file to static/uploads/banners.
    Returns relative path for DB storage.
    """
    return _save_static_upload(file, "banners")


def save_store_image(file: Optional[FileStorage]) -> Optional[str]:
    """
    Save a store branding image (logo, hero) to static/uploads/stores.
    """
    return _save_static_upload(file, "stores")
