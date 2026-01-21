from flask import redirect, url_for, request, render_template
from app.web import web_bp
from app.utils.cart import add_to_cart, remove_from_cart
from app.services.cart_service import build_cart_items


@web_bp.route("/cart")
def cart():
    data = build_cart_items()
    return render_template(
        "checkout/cart.html",
        cart_items=data["items"],
        cart_total=data["total"],
    )


@web_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id: int):
    qty = request.form.get("quantity", 1, type=int)
    add_to_cart(product_id, qty)
    return redirect(url_for("web.cart"))


@web_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def cart_remove(product_id: int):
    remove_from_cart(product_id)
    return redirect(url_for("web.cart"))
