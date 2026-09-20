from typing import Any

from flask import abort, flash, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.extensions.db import db
from app.models.product import Product
from app.models.tenant import Tenant
from app.models.tenant_banner import TenantBanner
from app.models.testimonial import Testimonial
from app.models.user import User
from app.store.routes import render_store_home
from app.utils.uploads import save_banner_image, save_store_image
from app.web import bp, web_bp
from app.web.forms import (
    SignupForm,
    StoreSettingsForm,
    TenantBannerForm,
    TestimonialForm,
)


def add_error(field: Any, message: str) -> None:
    """Attach a server-side validation error to a WTForms field."""
    field.errors = [*field.errors, message]


# -------------------------------
# Platform (tola) pages
# -------------------------------

@web_bp.route("/")
def home() -> str:
    # A subdomain request (mystore.example.com) renders that store directly
    tenant: Tenant | None = getattr(g, "tenant", None)
    if tenant is not None:
        return render_store_home(tenant)

    # Otherwise show the platform landing page with a few live stores
    stores = (
        db.session.query(Tenant, func.count(Product.id))
        .join(Product, (Product.tenant_id == Tenant.id) & Product.is_active.is_(True))
        .group_by(Tenant.id)
        .order_by(func.count(Product.id).desc())
        .limit(6)
        .all()
    )

    return render_template("platform/landing.html", stores=stores)


@web_bp.route("/signup", methods=["GET", "POST"])
def signup() -> Any:
    """
    Self-serve onboarding: create a store (tenant) and its owner in one go.
    """
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = SignupForm()

    if form.validate_on_submit():
        store_name = (form.store_name.data or "").strip()
        slug = (form.slug.data or "").strip().lower()
        email = (form.email.data or "").strip().lower()

        taken = False
        if Tenant.query.filter(func.lower(Tenant.name) == store_name.lower()).first():
            add_error(form.store_name, "A store with this name already exists.")
            taken = True
        if Tenant.query.filter_by(slug=slug).first():
            add_error(form.slug, "This link is already taken.")
            taken = True
        if User.query.filter_by(email=email).first():
            add_error(form.email, "An account with this email already exists.")
            taken = True

        if not taken:
            tenant = Tenant()
            tenant.name = store_name
            tenant.slug = slug
            tenant.hero_theme = "dark"
            tenant.contact_email = email

            user = User()
            user.email = email
            user.set_password(form.password.data or "")
            user.is_admin = True
            user.is_tenant_admin_flag = True
            user.tenant = tenant

            db.session.add_all([tenant, user])

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("That store name, link or email was just taken. Please try another.", "danger")
                return render_template("auth/signup.html", form=form), 409

            login_user(user)
            flash("Your store is live! Add a category and your first product to get started.", "success")
            return redirect(url_for("admin.dashboard"))

    return render_template("auth/signup.html", form=form)


@web_bp.route("/testimonial/new", methods=["GET", "POST"])
@login_required
def new_testimonial():
    if not current_user.is_admin:
        flash("You are not authorised.", "danger")
        return redirect(url_for("web.home"))

    form = TestimonialForm()
    if form.validate_on_submit():
        testimonial = Testimonial()
        testimonial.author_name = form.author_name.data or "Anonymous"
        testimonial.content = form.content.data or ""
        testimonial.rating = form.rating.data or 5
        testimonial.tenant_id = current_user.tenant_id  # ensure tenant scoping

        db.session.add(testimonial)
        db.session.commit()
        flash("Testimonial added to your storefront.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/testimonials/form.html", form=form)


# -------------------------------
# Store owner: customisation & banners
# -------------------------------

@bp.before_request
@login_required
def require_store_owner() -> None:
    """
    Every /admin/tenant route acts on the signed-in owner's own store.
    """
    if not current_user.is_admin or current_user.tenant is None:
        abort(403)


def get_current_tenant() -> Tenant:
    return current_user.tenant


@bp.route("/settings", methods=["GET", "POST"])
def store_settings() -> Any:
    tenant: Tenant = get_current_tenant()
    form = StoreSettingsForm(obj=tenant)

    if form.validate_on_submit():
        name = (form.name.data or "").strip()
        slug = (form.slug.data or "").strip().lower()

        clash = False
        if Tenant.query.filter(func.lower(Tenant.name) == name.lower(), Tenant.id != tenant.id).first():
            add_error(form.name, "Another store already uses this name.")
            clash = True
        if Tenant.query.filter(Tenant.slug == slug, Tenant.id != tenant.id).first():
            add_error(form.slug, "This link is already taken.")
            clash = True

        if not clash:
            slug_changed = slug != tenant.slug

            tenant.name = name
            tenant.slug = slug
            tenant.tagline = (form.tagline.data or "").strip() or None
            tenant.about = (form.about.data or "").strip() or None
            tenant.accent_color = (form.accent_color.data or "").lower()
            tenant.hero_theme = form.hero_theme.data or "dark"
            tenant.currency_symbol = form.currency_symbol.data or "₦"
            tenant.hero_title = (form.hero_title.data or "").strip() or None
            tenant.hero_subtitle = (form.hero_subtitle.data or "").strip() or None
            tenant.contact_email = (form.contact_email.data or "").strip() or None
            tenant.contact_phone = (form.contact_phone.data or "").strip() or None
            tenant.instagram_url = (form.instagram_url.data or "").strip() or None

            if form.remove_logo.data:
                tenant.logo = None
            new_logo = save_store_image(form.logo.data)
            if new_logo:
                tenant.logo = new_logo

            if form.remove_hero_image.data:
                tenant.hero_image = None
            new_hero = save_store_image(form.hero_image.data)
            if new_hero:
                tenant.hero_image = new_hero

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("That name or link was just taken. Please try another.", "danger")
                return render_template("admin/tenant/settings.html", form=form, tenant=tenant), 409

            if slug_changed:
                flash("Saved. Your store link changed — share the new one below.", "warning")
            else:
                flash("Store updated.", "success")
            return redirect(url_for("tenant_content.store_settings"))

    return render_template("admin/tenant/settings.html", form=form, tenant=tenant)


@bp.route("/billboard", methods=["GET", "POST"])
def edit_billboard() -> Any:
    # Theme now lives on the full settings page
    return redirect(url_for("tenant_content.store_settings"))


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


@bp.route("/banners/create", methods=["GET", "POST"])
def banner_create() -> Any:
    tenant: Tenant = get_current_tenant()
    form = TenantBannerForm()

    if request.method == "GET":
        form.is_active.data = True

    if form.validate_on_submit():
        image_path = save_banner_image(form.image_file.data)
        background_path = save_banner_image(form.background_file.data)

        banner = TenantBanner()
        banner.tenant_id = tenant.id
        banner.title = form.title.data or "New Banner"
        banner.subtitle = form.subtitle.data or ""
        banner.image_file = image_path or ""  # column is NOT NULL
        banner.background_image = background_path
        banner.hover_effect = form.hover_effect.data or "zoom"
        banner.cta_text = form.cta_text.data or ""
        banner.cta_url = form.cta_url.data or ""
        banner.bg_color = form.bg_color.data or ""
        banner.text_color = form.text_color.data or "#000000"
        banner.order = form.order.data or 0
        banner.is_active = form.is_active.data

        db.session.add(banner)
        db.session.commit()

        flash("Banner created successfully.", "success")
        return redirect(url_for("tenant_content.banner_list"))

    return render_template(
        "admin/tenant/banner_form.html",
        form=form,
        title="Create Banner",
    )


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
            banner.image_file = new_image

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
