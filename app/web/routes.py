from flask import render_template, request, flash, url_for, send_from_directory, redirect
from app.models.product import Product
from app.models.testimonial import Testimonial
from app.models.blog import Blog
from app.web import web_bp, web_blog_bp
from app.extensions.db import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from typing import List
from app.models.category import Category
from app.web.forms import TestimonialForm
from flask_login import login_required, current_user


@web_bp.route("/")
def home():
    products = Product.query.limit(8).all()
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).limit(5).all()
    return render_template("index.html", products=products, testimonials=testimonials)

@web_bp.route("/testimonial/new", methods=["GET", "POST"])
@login_required  # optional, depending on whether you want to allow anonymous testimonials
def new_testimonial():
    if not current_user.is_admin:
        flash("You are not authorised.", "danger")
        return redirect(url_for("web.home"))
    
    form = TestimonialForm()
    if form.validate_on_submit():
        testimonial = Testimonial()
        testimonial.author_name=form.author_name.data or "Anonymous"
        testimonial.content=form.content.data or ""
        testimonial.rating=form.rating.data or 5
        testimonial.tenant_id = current_user.tenant_id  # ensure tenant scoping
        
        db.session.add(testimonial)
        db.session.commit()
        flash("Thank you! Your testimonial has been submitted.", "success")
        return redirect(url_for("web.home"))

    return render_template("new_testimonial.html", form=form)

@web_bp.route("/user", methods=["GET"])
@login_required  # optional
def user() -> str:
    return render_template("web/user.html")

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
def list_blogs():
    # If user is logged in, filter by tenant
    tenant_id = getattr(current_user, "tenant_id", None)
    
    query = Blog.query.order_by(Blog.created_at.desc())

    if tenant_id:
        query = query.filter_by(tenant_id=tenant_id)
    
    blogs = query.all()
    
    return render_template("blog.html", blogs=blogs)


@web_bp.route("/blogs/<slug>")
def blog_detail(slug: str):
    tenant_id = getattr(current_user, "tenant_id", None)

    blog = (
        Blog.query
        .filter_by(slug=slug)
        .first_or_404()
    )

    return render_template("/detail.html", blog=blog)


@web_bp.route("/shop")
def shop():
    """
    Shop page – lists available products.
    """
    try:
        # Defensive query: avoid breaking the page if DB is empty
        products: list[Product] = Product.query.limit(24).all()

        return render_template("shop.html", products=products)

    except SQLAlchemyError as exc:
        # Basic error handling to avoid crashing the UI
        return f"Database error loading shop: {exc}", 500
 

@web_bp.route("/search", methods=["GET"])
def search():
    query: str = request.args.get("q", "").strip()

    # Empty query → no DB hit
    if not query:
        return render_template(
            "web/search.html",
            query=query,
            products=[],
            categories=[],
        )

    # ----------------------------
    # Build product search filters
    # ----------------------------
    product_filters = []

    if hasattr(Product, "name"):
        product_filters.append(Product.name.ilike(f"%{query}%"))

    if hasattr(Product, "description"):
        product_filters.append(Product.description.ilike(f"%{query}%"))

    products: List[Product] = []
    if product_filters:
        products = (
            Product.query
            .filter(or_(*product_filters))  # ✅ only SQL expressions
            .limit(24)
            .all()
        )

    # ----------------------------
    # Category search
    # ----------------------------
    categories: List[Category] = []
    if hasattr(Category, "name"):
        categories = (
            Category.query
            .filter(Category.name.ilike(f"%{query}%"))
            .limit(10)
            .all()
        )

    return render_template(
        "web/search.html",
        query=query,
        products=products,
        categories=categories,
    )
