from app.models.product_variant import ProductVariant
from app.extensions.db import db
from app.models.inventory import Inventory


def get_stock_status(stock_quantity: int) -> str:
    """
    Returns a semantic stock status used by UI badges.
    """
    if stock_quantity <= 0:
        return "out"
    if stock_quantity <= 10:
        return "low"
    return "ok"


def decrease_stock(tenant_id: int, variant_id: int, quantity: int) -> None:
    """
    Safely decreases stock for a tenant-scoped variant.
    """

    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    inventory = Inventory.query.filter_by(
        tenant_id=tenant_id,
        variant_id=variant_id
    ).with_for_update().first()

    if not inventory:
        raise ValueError("Inventory record not found")

    if inventory.quantity_available < quantity:
        raise ValueError("Insufficient stock")

    inventory.quantity_available -= quantity
    db.session.commit()


def increase_stock(tenant_id: int, variant_id: int, quantity: int) -> None:
    """
    Safely increases stock for a tenant-scoped variant.
    """

    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    inventory = Inventory.query.filter_by(
        tenant_id=tenant_id,
        variant_id=variant_id
    ).first()

    if not inventory:
        raise ValueError("Inventory record not found")

    inventory.quantity_available += quantity
    db.session.commit()


def apply_inventory_delta(variant: ProductVariant, delta: int) -> None:
    """
    Apply a stock change to a product variant.

    - Positive delta increases stock
    - Negative delta decreases stock
    - Prevents stock from going below zero
    """

    if variant is None:
        raise ValueError("Variant is required")

    if delta == 0:
        raise ValueError("Delta cannot be zero")

    new_quantity: int = variant.stock_quantity + delta

    # Prevent negative stock
    if new_quantity < 0:
        raise ValueError("Inventory cannot go below zero")

    variant.stock_quantity = new_quantity

    db.session.add(variant)
    db.session.commit()

