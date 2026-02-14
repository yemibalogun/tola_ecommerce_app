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

def save_banner_image(file: Optional[FileStorage]) -> Optional[str]:
    """
    Save uploaded file to static/uploads/banners.
    Returns relative path for DB storage.
    """

    if file is None or file.filename == "":
        return None

    try:
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "banners",
        )

        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, secure_filename(filename))

        file.save(file_path)

        # Store relative path in DB
        return f"uploads/banners/{filename}"

    except Exception:
        return None