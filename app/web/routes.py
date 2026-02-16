from flask import abort, render_template, g, request, flash, url_for, send_from_directory, redirect
from app.models.product import Product
from app.models.testimonial import Testimonial
from app.models.blog import Blog
from app.models.category import Category
from app.models.tenant import Tenant
from app.models.tenant_banner import TenantBanner
from app.web.forms import TestimonialForm, BillboardForm, TenantBannerForm
from app.web import web_bp
from app.web import bp
from app.extensions.db import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from typing import List, Any, Dict
from app.utils.uploads import save_banner_image
from flask_login import login_required, current_user
import random



@web_bp.route("/")
def home() -> str:
    # Tenant already loaded in before_request
    tenant: Tenant | None = getattr(g, "tenant", None)

    # Development fallback
    if tenant is None:
        tenant = Tenant.query.first()

    if tenant is None:
        abort(404)
    # --- General products for other homepage sections ---
    products: List[Product] = (
        Product.query
        .limit(5)
        .all()
    )
    
    # --- Categories that contain at least 1 product ---
    categories: List[Category] = (
        Category.query
        .join(Product)
        .options(selectinload(Category.products))
        .group_by(Category.id)
        .having(func.count(Product.id) > 0)
        .order_by(func.random())
        .limit(2)
        .all()
    )

    category_sections: Dict[str, List[Product]] = {}

    if categories:
        selected_categories = random.sample(
            categories,
            k=min(2, len(categories)),
        )

        for category in selected_categories:

            name: str | None = category.name
            if not name:
                continue

            products_categories: List[Product] = (
                Product.query
                .filter(Product.category_id == category.id)
                .order_by(func.random())
                .limit(4)
                .all()
            )

            if products_categories:
                category_sections[name] = products_categories

    testimonials = (
        Testimonial.query
        .order_by(Testimonial.created_at.desc())
        .limit(5)
        .all()
    )

    blogs = (
        Blog.query
        .order_by(Blog.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "index.html",
        products=products,  # 🔹 still available for other sections
        tenant=tenant,
        category_sections=category_sections,
        testimonials=testimonials,
        blogs=blogs,
    )


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
    products = Product.query.filter_by(tenant_id=g.tenant.id)

    return render_template("layouts/product/list.html", products=products)

@web_bp.route("/product/<slug>")
def product_detail(slug: str):
    product = Product.query.filter_by(slug=slug).first_or_404()

    if product is None:
        abort(404)
    return render_template(
        "layouts/product/detail.html", 
        product=product
    )

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

def get_current_tenant() -> Tenant:
    """
    Replace with your tenant resolution logic.
    """
    tenant: Tenant | None = Tenant.query.first()

    if tenant is None:
        raise RuntimeError("No tenant found.")

    return tenant


# -------------------------------
# Billboard Settings
# -------------------------------

@bp.route("/billboard", methods=["GET", "POST"])
def edit_billboard() -> Any:
    tenant: Tenant = get_current_tenant()
    form = BillboardForm(obj=tenant)

    if form.validate_on_submit():
        tenant.hero_theme = form.hero_theme.data

        db.session.commit()
        flash("Billboard updated successfully.", "success")

        return redirect(url_for("tenant_content.edit_billboard"))

    return render_template(
        "admin/tenant/billboard.html",
        form=form,
        tenant=tenant,
    )


# -------------------------------
# Banner List
# -------------------------------

@bp.route("/banners")
def banner_list() -> Any:
    tenant: Tenant = get_current_tenant()

    banners = (
        TenantBanner.query
        .filter_by(tenant_id=tenant.id)
        .order_by(TenantBanner.order.asc())
        .all()
    )

    return render_template(
        "admin/tenant/banner_list.html",
        banners=banners,
    )


# -------------------------------
# Create Banner
# -------------------------------

@bp.route("/banners/create", methods=["GET", "POST"])
def banner_create() -> Any:
    tenant: Tenant = get_current_tenant()
    form = TenantBannerForm()

    if form.validate_on_submit():
        image_path = save_banner_image(form.image_file.data)
        background_path = save_banner_image(form.background_file.data)

        banner = TenantBanner()
        banner.tenant_id=tenant.id
        banner.title=form.title.data or "New Banner"
        banner.subtitle=form.subtitle.data or ""
        banner.image_file=image_path  # stored relative path
        banner.background_image=background_path
        banner.hover_effect=form.hover_effect.data or ""
        banner.cta_text=form.cta_text.data or ""
        banner.cta_url=form.cta_url.data or ""
        banner.bg_color=form.bg_color.data or ""
        banner.text_color=form.text_color.data or "#000000"
        banner.order=form.order.data or 0
        banner.is_active=form.is_active.data
        
        db.session.add(banner)
        db.session.commit()

        flash("Banner created successfully.", "success")
        return redirect(url_for("tenant_content.banner_list"))

    return render_template(
        "admin/tenant/banner_form.html",
        form=form,
        title="Create Banner",
    )


# -------------------------------
# Edit Banner
# -------------------------------

@bp.route("/banners/<int:banner_id>/edit", methods=["GET", "POST"])
def banner_edit(banner_id: int) -> Any:
    tenant: Tenant = get_current_tenant()

    banner = TenantBanner.query.filter_by(
        id=banner_id,
        tenant_id=tenant.id,
    ).first_or_404()

    form = TenantBannerForm(obj=banner)

    if form.validate_on_submit():
        new_image = save_banner_image(form.image_file.data)
        new_background = save_banner_image(form.background_file.data)

        # Only update if new file uploaded
        if new_image:
            banner.image_path = new_image

        if new_background:
            banner.background_image = new_background

        banner.title = form.title.data
        banner.subtitle = form.subtitle.data
        banner.hover_effect = form.hover_effect.data
        banner.cta_text = form.cta_text.data
        banner.cta_url = form.cta_url.data
        banner.bg_color = form.bg_color.data
        banner.text_color = form.text_color.data
        banner.order = form.order.data or 0
        banner.is_active = form.is_active.data

        db.session.commit()
        flash("Banner updated successfully.", "success")

        return redirect(url_for("tenant_content.banner_list"))

    return render_template(
        "admin/tenant/banner_form.html",
        form=form,
        banner=banner,
        title="Edit Banner",
    )


# -------------------------------
# Delete Banner
# -------------------------------

@bp.route("/banners/<int:banner_id>/delete", methods=["POST"])
def banner_delete(banner_id: int) -> Any:
    tenant: Tenant = get_current_tenant()

    banner = TenantBanner.query.filter_by(
        id=banner_id,
        tenant_id=tenant.id,
    ).first_or_404()

    db.session.delete(banner)
    db.session.commit()

    flash("Banner deleted.", "info")
    return redirect(url_for("tenant_content.banner_list"))