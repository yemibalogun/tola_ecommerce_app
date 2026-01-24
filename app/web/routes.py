from flask import render_template, request, send_from_directory
from app.models.product import Product
from app.web import web_bp

@web_bp.route("/test-css")
def test_css():
    return send_from_directory("static/css", "style.css")

@web_bp.route("/")
def home():
    products = Product.query.limit(8).all()
    return render_template("index.html", products=products)

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

@web_bp.route("/about")
def about():
    """
    Renders the About page.
    No DB access required.
    """
    try:
        return render_template("about.html")
    except Exception as exc:
        # Basic safety net: surface a clean error instead of a hard crash
        return f"Error loading About page: {exc}", 500

from flask import Blueprint, render_template, request

web_bp = Blueprint("web", __name__)

@web_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """
    Renders the Contact page.
    Handles basic POST submission without persistence.
    """
    try:
        if request.method == "POST":
            # Basic form extraction with safe defaults
            name: str = request.form.get("name", "").strip()
            email: str = request.form.get("email", "").strip()
            message: str = request.form.get("message", "").strip()

            # Minimal validation (no DB / email integration yet)
            if not name or not email or not message:
                return render_template(
                    "contact.html",
                    error="All fields are required."
                )

            # Placeholder for future logic:
            # - save to DB
            # - send email
            # - push to queue
            return render_template(
                "contact.html",
                success="Thanks for reaching out. We’ll get back to you shortly."
            )

        return render_template("contact.html")

    except Exception as exc:
        return f"Error loading Contact page: {exc}", 500


@web_bp.route("/blogs")
def blog():
    """
    Blog landing page.
    Currently renders static posts.
    Can be upgraded to DB-backed posts later.
    """
    try:
        # Temporary static data to avoid DB coupling for now
        posts: list[dict[str, str]] = [
            {
                "title": "Building Scalable E-commerce with Flask",
                "excerpt": "Lessons learned while designing a modular Flask-based SaaS architecture.",
                "slug": "scalable-ecommerce-with-flask",
                "date": "Jan 2026",
            },
            {
                "title": "Why HTMX is a Game Changer",
                "excerpt": "Reducing frontend complexity without sacrificing interactivity.",
                "slug": "why-htmx-matters",
                "date": "Jan 2026",
            },
        ]

        return render_template("blog.html", posts=posts)

    except Exception as exc:
        return f"Error loading Blog page: {exc}", 500