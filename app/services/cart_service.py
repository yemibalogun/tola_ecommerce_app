from typing import Dict, List, TypedDict
from app.extensions import db
from app.models.product import Product
from app.utils.cart import get_cart


class CartItem(TypedDict):
    product: Product
    quantity: int
    line_total: float


class CartData(TypedDict):
    items: List[CartItem]
    total: float


def build_cart_items() -> CartData:
    """
    Hydrates session cart with Product objects.
    Prices are always fetched from DB to prevent tampering.
    """
    cart = get_cart()

    # Edge case: empty cart
    if not cart:
        return {"items": [], "total": 0.0}

    try:
        product_ids = [int(pid) for pid in cart.keys()]
    except ValueError:
        # Edge case: corrupted session data
        return {"items": [], "total": 0.0}

    products = (
        db.session.query(Product)
        .filter(Product.id.in_(product_ids))
        .all()
    )

    items: List[CartItem] = []
    total: float = 0.0

    for product in products:
        qty = cart.get(str(product.id), 0)

        # Guard: product removed or invalid quantity
        if qty <= 0:
            continue

        line_total = float(product.price) * qty
        total += line_total

        items.append({
            "product": product,
            "quantity": qty,
            "line_total": line_total,
        })

    return {
        "items": items,
        "total": round(total, 2),
    }
