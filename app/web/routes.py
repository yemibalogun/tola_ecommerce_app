from flask import render_template, request, send_from_directory
from models.product import Product
from app.web import web_bp

@web_bp.route("/test-css")
def test_css():
    return send_from_directory("static/css", "style.css")

@web_bp.route("/")
def home():
    products = Product.query.limit(8).all()
    return render_template("/index.html", products=products)

@web_bp.route("/products")
def product_list():
    products = Product.query.all()
    return render_template("layouts/product/list.html", products=products)

@web_bp.route("/product/<slug>")
def product_detail(slug: str):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template("layouts/product/detail.html", product= product)

@web_bp.route("/cart")
def cart():
    cart_items = []  # replace with real cart session logic
    cart_total = 0
    return render_template(
        "checkout/cart.html",
        cart_items=cart_items,
        cart_total=cart_total
    )

@web_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items = []
    cart_total = 0

    if request.method == "POST":
        # handle order creation here
        pass

    return render_template(
        "checkout/checkout.html",
        cart_items=cart_items,
        cart_total=cart_total
    )
