from app.extensions.db import db
from app.models.product_variant import ProductVariant


def decrease_stock(variant_id: int, quantity: int) -> None:
    variant = ProductVariant.query.get_or_404(variant_id)

    # Prevent overselling
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    if variant.stock_quantity < quantity:
        raise ValueError("Insufficient stock")

    variant.stock_quantity -= quantity
    db.session.commit()


def increase_stock(variant_id: int, quantity: int) -> None:
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    variant = ProductVariant.query.get_or_404(variant_id)
    variant.stock_quantity += quantity
    db.session.commit()
