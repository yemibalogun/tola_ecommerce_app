from typing import List
from flask import render_template, redirect, url_for, flash
from app.admin import admin_bp
from app.admin.forms import ProductForm
from app.admin.services import save_product_image, get_products
from app.utils.slug import unique_slug
from app.extensions.db import db
from app.models.product import Product
from app.models.category import Category
from flask_login import current_user
from app.admin.services import PRODUCT_IMAGE_DIR


@admin_bp.route("/products")
def products() -> str:
    products: List[Product] = (
        Product.query
        .filter_by(tenant_id=current_user.tenant_id)
        .order_by(Product.id.desc())
        .all()
    )
    return render_template("admin/products/list.html", products=products)


@admin_bp.route("/products/create", methods=["GET", "POST"])
def create_product():
    form = ProductForm()
    form.category_id.choices = [
        (c.id, c.name)
        for c in Category.query.filter_by(
            tenant_id=current_user.tenant_id
        ).all()
    ]

    if form.validate_on_submit():
        name_raw: str | None = form.name.data

        # WTForms may still return None even with DataRequired
        if not name_raw:
            flash("Product name is required", "error")
            return render_template("admin/products/create.html", form=form)

        name: str = name_raw.strip()

        product = Product()
        product.name=name
        product.slug=unique_slug(Product, name)
        product.description=form.description.data
        product.price=form.price.data
        product.is_active=form.is_active.data
        product.tenant_id=current_user.tenant_id
        product.category_id=form.category_id.data or None
        
        image_path = save_product_image(
            form.image.data,
            PRODUCT_IMAGE_DIR,
        )
        if image_path:
            product.image = image_path  

        db.session.add(product)
        db.session.commit()

        flash("Product created", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/products/create.html", form=form)


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id: int):
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    form = ProductForm(obj=product)
    form.category_id.choices = [
        (c.id, c.name)
        for c in Category.query.filter_by(
            tenant_id=current_user.tenant_id
        ).all()
    ]

    if form.validate_on_submit():
        name_raw: str | None = form.name.data
        if not name_raw:
            flash("Product name is required", "error")
            return render_template(
                "admin/products/edit.html",
                form=form,
                product=product,
            )

        name: str = name_raw.strip()
        old_name: str = product.name

        product.name = name
        product.description = form.description.data
        product.price = form.price.data
        product.is_active = form.is_active.data
        product.category_id = form.category_id.data or None

        # Only regenerate slug if name actually changed
        if name != product.name:
            product.slug = unique_slug(Product, name)

        image_path = save_product_image(
            form.image.data,
            PRODUCT_IMAGE_DIR,
        )
        if image_path:
            product.image = image_path

        db.session.commit()
        flash("Product updated", "success")
        return redirect(url_for("admin.products"))

    return render_template(
        "admin/products/edit.html",
        form=form,
        product=product,
    )


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id: int):
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted", "success")
    return redirect(url_for("admin.products"))
