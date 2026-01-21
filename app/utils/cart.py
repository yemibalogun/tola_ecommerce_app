from typing import Dict, List
from app.models.product import Product
from app.extensions.db import db
from app.utils.cart import get_cart
from flask import session

Cart = Dict[str, int]


def get_cart() -> Cart:
    """
    Safely get cart from session.
    Ensures correct default and type.
    """
    cart = session.get("cart")

    # Edge case: corrupted or missing cart
    if not isinstance(cart, dict):
        if not isinstance(cart, dict):
        session["cart"] = {}
        return session["cart"]

    return cart


def add_to_cart(product_id: int, quantity: int = 1) -> None:
    """
    Add or increment product in cart.
    """
    if quantity <= 0:
        return  # invalid quantity guard

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
    """
    Converts session cart into renderable objects.
    """
    cart = get_cart()
    if not cart:
        return {"items": [], "total": 0}

    product_ids = [int(pid) for pid in cart.keys()]

    products = (
        db.session.query(Product)
        .filter(Product.id.in_(product_ids))
        .all()
    )

    items = []
    total = 0

    for product in products:
        qty = cart.get(str(product.id), 0)

        # Edge case: product removed but still in session
        if qty <= 0:
            continue

        line_total = product.price * qty
        total += line_total

        items.append({
            "product": product,
            "quantity": qty,
            "line_total": line_total,
        })

    return {"items": items, "total": total}
