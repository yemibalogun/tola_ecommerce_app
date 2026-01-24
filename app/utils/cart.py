from typing import Dict, List
from flask import session
from app.extensions.db import db
from app.models.product import Product
from decimal import Decimal 
from sqlalchemy.orm import Mapped, mapped_column

Cart = Dict[str, int]


def get_cart() -> Cart:
    """
    Safely get cart from Flask session.
    Ensures correct default and type.
    """
    cart = session.get("cart")

    # Edge case: corrupted or missing cart
    if not isinstance(cart, dict):
        session["cart"] = {}
        return session["cart"]

    return cart


def add_to_cart(product_id: int, quantity: int = 1) -> None:
    """
    Add or increment product in cart.
    """
    if quantity <= 0:
        return  # guard invalid quantity

    cart = get_cart()
    pid = str(product_id)

    cart[pid] = cart.get(pid, 0) + quantity
    session.modified = True  # ensure session persistence


def remove_from_cart(product_id: int) -> None:
    """
    Remove product from cart.
    """
    cart = get_cart()
    cart.pop(str(product_id), None)
    session.modified = True


def clear_cart() -> None:
    """
    Empty cart completely.
    """
    session.pop("cart", None)
    session.modified = True


def build_cart_items() -> Dict[str, object]:
    cart = get_cart()

    if not cart:
        return {"items": [], "total": 0.0}

    try:
        product_ids = [int(pid) for pid in cart.keys()]
    except ValueError:
        return {"items": [], "total": 0.0}

    products = (
        db.session.query(Product)
        .filter(Product.id.in_(product_ids))
        .all()
    )

    items: List[Dict[str, object]] = []
    total: Decimal = Decimal("0.00")

    for product in products:
        qty = cart.get(str(product.id), 0)
        if qty <= 0:
            continue

        price: Decimal = product.price
        line_total: Decimal = price * Decimal(qty)

        total += line_total

        items.append({
            "product": product,
            "quantity": qty,
            "line_total": float(line_total),
        })

    return {
        "items": items,
        "total": float(total.quantize(Decimal("0.01"))),
    }