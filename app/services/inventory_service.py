from app.extensions.db import db
from app.models.product_variant import ProductVariant


def apply_inventory_delta(variant: ProductVariant, delta: int) -> None:
    """
    Apply inventory change safely.
    """

    if delta == 0:
        return # no-op guard
    
    # Clamp to zero to avoid negative stock
    variant.stock_quantity = max(0, variant.stock_quantity + delta)
    db.session.commit()
