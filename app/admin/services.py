from pathlib import Path
from typing import Optional
from werkzeug.datastructures import FileStorage

BASE_DIR: Path = Path(__file__).resolve().parents[2]
PRODUCT_IMAGE_DIR: Path = BASE_DIR / "static" / "uploads" / "products"

def save_product_image(file: FileStorage | None, 
                       upload_dir: Path,
                    ) -> Optional[str]:
    """
    Saves an uploaded product image to disk.

    Returns the filename if successful, otherwise None.
    """

    # Defensive checks to avoid runtime errors
    if not file or not file.filename:
        return None

    try:
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename: str = file.filename
        file_path = upload_dir / filename

        # Save file to disk
        file.save(file_path)

        return f"uploads/products/{filename}"
    except Exception:
        # In production, log this exception
        return None


def get_products() -> list[dict]:
    return []
