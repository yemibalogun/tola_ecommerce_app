from typing import Any, Dict, List

from flask import abort, current_app, flash, g, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from app.extensions.db import db
from app.models.blog import Blog
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.tenant import Tenant
from app.models.testimonial import Testimonial
from app.store import store_bp
from app.utils.cart import (
    add_to_cart,
    build_cart_items,
    clear_cart,
    remove_from_cart,
    set_quantity,
)


# -------------------------------
# Tenant resolution
# -------------------------------

@store_bp.url_value_preprocessor
def load_store(endpoint: str | None, values: Dict[str, Any] | None) -> None:
    """
    Pull <store_slug> out of the URL and load that tenant into g.tenant.
    Unknown slugs 404 so one store can never render another's data.
    """
    slug = values.pop("store_slug", None) if values else None
    tenant = Tenant.query.filter_by(slug=slug).first() if slug else None

    if tenant is None:
        abort(404)

    g.tenant = tenant


@store_bp.url_defaults
def add_store_slug(endpoint: str, values: Dict[str, Any]) -> None:
    """
    Let templates call url_for('store.products') without repeating the slug.
    """
    if "store_slug" in values:
        return

    tenant: Tenant | None = getattr(g, "tenant", None)
    if tenant is not None:
        values["store_slug"] = tenant.slug


def _active_products():
    return Product.query.filter_by(tenant_id=g.tenant.id, is_active=True)


def _categories_with_counts(tenant_id: int) -> List[Dict[str, Any]]:
    """
    Categories that contain at least one active product, with a count and a
    cover image taken from one of their products.
    """
    rows = (
        db.session.query(Category, func.count(Product.id))
        .join(Product, Product.category_id == Category.id)
        .filter(
            Category.tenant_id == tenant_id,
            Product.tenant_id == tenant_id,
            Product.is_active.is_(True),
        )
        .group_by(Category.id)
        .order_by(func.count(Product.id).desc(), Category.name.asc())
        .all()
    )

    categories: List[Dict[str, Any]] = []
    for category, count in rows:
        cover = (
            Product.query
            .filter(
                Product.category_id == category.id,
                Product.tenant_id == tenant_id,
                Product.is_active.is_(True),
                Product.image.isnot(None),
            )
            .order_by(Product.created_at.desc())
            .first()
        )
        categories.append({"category": category, "count": count, "cover": cover})

    return categories


# -------------------------------
# Pages
# -------------------------------

def render_store_home(tenant: Tenant) -> str:
    """
    Shared by /store/<slug>/ and by subdomain requests to /.
    """
    featured: List[Product] = (
        Product.query
        .filter_by(tenant_id=tenant.id, is_active=True)
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )

    # Hero slides: owner-managed banners win; otherwise build one from settings
    banners = sorted(
        (b for b in tenant.banners if b.is_active),
        key=lambda b: b.order or 0,
    )

    hero_fallback_image = tenant.hero_image or next(
        (p.image for p in featured if p.image), None
    )

    slides: List[Dict[str, Any]] = [
        {
            "title": b.title,
            "subtitle": b.subtitle,
            "cta_text": b.cta_text or "Shop Now",
            "cta_url": b.cta_url or None,
            "image": b.image_file or hero_fallback_image,
        }
        for b in banners
    ] or [
        {
            "title": tenant.display_hero_title,
            "subtitle": tenant.display_hero_subtitle,
            "cta_text": "Shop Now",
            "cta_url": None,
            "image": hero_fallback_image,
        }
    ]

    testimonials = (
        Testimonial.query
        .filter_by(tenant_id=tenant.id)
        .order_by(Testimonial.created_at.desc())
        .limit(3)
        .all()
    )

    blogs = (
        Blog.query
        .filter_by(tenant_id=tenant.id)
        .order_by(Blog.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "store/home.html",
        slides=slides,
        featured=featured,
        categories=_categories_with_counts(tenant.id)[:3],
        testimonials=testimonials,
        blogs=blogs,
    )


@store_bp.route("/")
def home() -> str:
    return render_store_home(g.tenant)


@store_bp.route("/products")
def products() -> str:
    query: str = request.args.get("q", "").strip()
    category_slug: str = request.args.get("category", "").strip()
    sort: str = request.args.get("sort", "new")

    q = _active_products()
    active_category: Category | None = None

    if category_slug:
        active_category = Category.query.filter_by(
            tenant_id=g.tenant.id, slug=category_slug
        ).first()
        if active_category is not None:
            q = q.filter(Product.category_id == active_category.id)

    if query:
        like = f"%{query}%"
        q = q.filter(or_(Product.name.ilike(like), Product.description.ilike(like)))

    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    else:
        sort = "new"
        q = q.order_by(Product.created_at.desc())

    return render_template(
        "store/products.html",
        products=q.all(),
        categories=_categories_with_counts(g.tenant.id),
        active_category=active_category,
        query=query,
        sort=sort,
    )


@store_bp.route("/products/<slug>")
def product_detail(slug: str) -> str:
    product: Product = _active_products().filter_by(slug=slug).first_or_404()

    related: List[Product] = []
    if product.category_id:
        related = (
            _active_products()
            .filter(Product.category_id == product.category_id, Product.id != product.id)
            .order_by(func.random())
            .limit(4)
            .all()
        )

    return render_template(
        "store/product_detail.html",
        product=product,
        related=related,
    )


# -------------------------------
# Cart & checkout
# -------------------------------

@store_bp.route("/cart")
def cart() -> str:
    return render_template("store/cart.html", cart=build_cart_items(g.tenant.id))


@store_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id: int) -> Any:
    product = _active_products().filter_by(id=product_id).first_or_404()
    qty = request.form.get("quantity", 1, type=int) or 1
    add_to_cart(g.tenant.id, product.id, qty)
    flash(f"{product.name} added to your cart.", "success")

    # Send the shopper back where they were unless they asked for the cart
    if request.form.get("next") == "cart":
        return redirect(url_for("store.cart"))
    return redirect(request.referrer or url_for("store.cart"))


@store_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def cart_update(product_id: int) -> Any:
    qty = request.form.get("quantity", 1, type=int)
    set_quantity(g.tenant.id, product_id, qty if qty is not None else 1)
    return redirect(url_for("store.cart"))


@store_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def cart_remove(product_id: int) -> Any:
    remove_from_cart(g.tenant.id, product_id)
    return redirect(url_for("store.cart"))


def place_order(tenant_id: int, cart: Dict[str, Any], customer: Dict[str, str]) -> Order:
    """
    Persist an order and its line items in a single transaction.

    Prices come from the freshly loaded products (never the session), and each
    line snapshots the price so later price changes don't rewrite history.
    Shoppers don't need an account, so user_id is only set when signed in.
    """
    order = Order()
    order.tenant_id = tenant_id
    order.status = "pending"
    order.total_amount = cart["total"]
    order.user_id = current_user.id if current_user.is_authenticated else None
    order.customer_name = customer["full_name"]
    order.customer_email = customer["email"]
    order.customer_phone = customer["phone"] or None
    order.shipping_address = customer["address"]

    for item in cart["items"]:
        line = OrderItem()
        line.tenant_id = tenant_id
        line.product_id = item["product"].id
        line.quantity = item["quantity"]
        line.unit_price = item["product"].price
        order.items.append(line)

    db.session.add(order)
    db.session.commit()

    current_app.logger.info(
        "Order %s placed for tenant %s (%s items)", order.id, tenant_id, len(order.items)
    )
    return order


@store_bp.route("/checkout", methods=["GET", "POST"])
def checkout() -> Any:
    cart = build_cart_items(g.tenant.id)

    if not cart["items"]:
        return redirect(url_for("store.cart"))

    errors: Dict[str, str] = {}
    form = {
        "full_name": request.form.get("full_name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "address": request.form.get("address", "").strip(),
    }

    if request.method == "POST":
        for field in ("full_name", "email", "address"):
            if not form[field]:
                errors[field] = "Required"
        if form["email"] and "@" not in form["email"]:
            errors["email"] = "Enter a valid email"

        if not errors:
            try:
                order = place_order(g.tenant.id, cart, form)
            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Checkout failed for tenant %s", g.tenant.id)
                flash("Something went wrong placing your order. Please try again.", "danger")
                return render_template("store/checkout.html", cart=cart, form=form, errors=errors), 500

            clear_cart(g.tenant.id)
            return render_template(
                "store/order_success.html",
                customer=form,
                cart=cart,
                order=order,
            )

    return render_template("store/checkout.html", cart=cart, form=form, errors=errors)


# -------------------------------
# Content pages
# -------------------------------

@store_bp.route("/about")
def about() -> str:
    return render_template("store/about.html")


@store_bp.route("/contact", methods=["GET", "POST"])
def contact() -> Any:
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in every field.", "danger")
            return render_template("store/contact.html"), 400

        # Placeholder: messages are not stored or emailed yet
        flash("Thanks for reaching out. We'll get back to you shortly.", "success")
        return redirect(url_for("store.contact"))

    return render_template("store/contact.html")


@store_bp.route("/blog")
def blog() -> str:
    posts = (
        Blog.query
        .filter_by(tenant_id=g.tenant.id)
        .order_by(Blog.created_at.desc())
        .all()
    )
    return render_template("store/blog.html", posts=posts)


@store_bp.route("/blog/<slug>")
def blog_post(slug: str) -> str:
    post = Blog.query.filter_by(tenant_id=g.tenant.id, slug=slug).first_or_404()
    return render_template("store/blog_post.html", post=post)
