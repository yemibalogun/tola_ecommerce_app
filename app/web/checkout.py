from flask import request, redirect, url_for
from app.utils.cart import clear_cart
from app.services.cart_service import build_cart_items


@web_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    data = build_cart_items()

    if request.method == "POST":
        if not data["items"]:
            return redirect(url_for("web.cart"))

        # Persist order here (Order, OrderItem models)

        clear_cart()  # 🔥 critical
        return redirect(url_for("web.order_success"))

    return render_template(
        "checkout/checkout.html",
        cart_items=data["items"],
        cart_total=data["total"],
    )
