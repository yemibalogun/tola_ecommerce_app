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

def get_stock_status(stock_quantity: int) -> str:
    """
    Returns a semantic stock status used by UI badges.
    """
    if stock_quantity <= 0:
        return "out"
    if stock_quantity <= 10:
        return "low"
    return "ok"
