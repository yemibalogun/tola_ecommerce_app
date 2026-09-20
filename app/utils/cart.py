from decimal import Decimal
from typing import Dict, List, TypedDict
from flask import session
from app.models.product import Product

# Session layout: {"carts": {"<tenant_id>": {"<product_id>": qty}}}
# Each store keeps its own cart so shoppers never see another store's items.
Cart = Dict[str, int]


class CartItem(TypedDict):
    product: Product
    quantity: int
    line_total: Decimal


class CartData(TypedDict):
    items: List[CartItem]
    total: Decimal
    count: int


def get_cart(tenant_id: int) -> Cart:
    """
    Safely get a store's cart from the Flask session.
    """
    carts = session.get("carts")

    # Edge case: corrupted or missing carts
    if not isinstance(carts, dict):
        carts = {}
        session["carts"] = carts

    cart = carts.get(str(tenant_id))
    if not isinstance(cart, dict):
        cart = {}
        carts[str(tenant_id)] = cart

    return cart


def add_to_cart(tenant_id: int, product_id: int, quantity: int = 1) -> None:
    """
    Add or increment product in cart.
    """
    if quantity <= 0:
        return  # guard invalid quantity

    cart = get_cart(tenant_id)
    pid = str(product_id)

    cart[pid] = min(cart.get(pid, 0) + quantity, 99)
    session.modified = True  # ensure session persistence


def set_quantity(tenant_id: int, product_id: int, quantity: int) -> None:
    """
    Set an exact quantity; zero or less removes the line.
    """
    if quantity <= 0:
        remove_from_cart(tenant_id, product_id)
        return

    get_cart(tenant_id)[str(product_id)] = min(quantity, 99)
    session.modified = True


def remove_from_cart(tenant_id: int, product_id: int) -> None:
    """
    Remove product from cart.
    """
    get_cart(tenant_id).pop(str(product_id), None)
    session.modified = True


def clear_cart(tenant_id: int) -> None:
    """
    Empty a store's cart completely.
    """
    carts = session.get("carts")
    if isinstance(carts, dict):
        carts.pop(str(tenant_id), None)
        session.modified = True


def cart_count(tenant_id: int) -> int:
    return sum(q for q in get_cart(tenant_id).values() if isinstance(q, int) and q > 0)


def build_cart_items(tenant_id: int) -> CartData:
    """
    Hydrates the session cart with Product objects.
    Prices are always fetched from DB to prevent tampering, and products are
    filtered by tenant so a cart can only ever hold this store's items.
    """
    cart = get_cart(tenant_id)

    if not cart:
        return {"items": [], "total": Decimal("0.00"), "count": 0}

    try:
        product_ids = [int(pid) for pid in cart.keys()]
    except ValueError:
        # Edge case: corrupted session data
        clear_cart(tenant_id)
        return {"items": [], "total": Decimal("0.00"), "count": 0}

    products = (
        Product.query
        .filter(
            Product.id.in_(product_ids),
            Product.tenant_id == tenant_id,
            Product.is_active.is_(True),
        )
        .all()
    )

    items: List[CartItem] = []
    total: Decimal = Decimal("0.00")
    count = 0

    for product in products:
        qty = cart.get(str(product.id), 0)
        if qty <= 0:
            continue

        line_total: Decimal = product.price * qty
        total += line_total
        count += qty

        items.append({
            "product": product,
            "quantity": qty,
            "line_total": line_total,
        })

    return {
        "items": items,
        "total": total.quantize(Decimal("0.01")),
        "count": count,
    }
