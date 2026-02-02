from flask import current_app, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.admin import admin_bp
from app.admin.forms import ProductVariantForm, InventoryAdjustForm
from app.admin.decorators import admin_required
from app.extensions.db import db
from app.models.product import Product
from app.models.product_variant import ProductVariant
import os 

@admin_bp.route("/products/<int:product_id>/variants")
def list_variants(product_id: int):
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    variants = ProductVariant.query.filter_by(
        product_id=product.id,
        tenant_id=current_user.tenant_id,
    ).all()

    return render_template(
        "admin/variants/list.html",
        product=product,
        variants=variants,
    )


@admin_bp.route(
    "/products/<int:product_id>/variants/create",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def create_variant(product_id: int):
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    form = ProductVariantForm()

    if form.validate_on_submit():
        try:
            variant = ProductVariant()
            variant.product_id=product.id
            variant.tenant_id=current_user.tenant_id
            variant.name=form.name.data.strip()
            variant.sku=form.sku.data.strip()
            variant.price_override=form.price_override.data
            variant.stock_quantity=form.stock_quantity.data

            # Handle image upload
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.image.data.save(upload_path)
                variant.image_filename = f"uploads/{filename}"

            db.session.add(variant)
            db.session.commit()

            flash("Variant created", "success")
            return redirect(
                url_for(
                    "admin.list_variants",
                    product_id=product.id,
                )
            )
        except Exception:
            db.session.rollback()
            flash("SKU already exists", "danger")

    return render_template(
        "admin/variants/variant_form.html",
        form=form,
        product=product,
    )


@admin_bp.route(
    "/variants/<int:variant_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def edit_variant(variant_id: int):
    variant = ProductVariant.query.filter_by(
        id=variant_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    form = ProductVariantForm(obj=variant)

    if form.validate_on_submit():
        variant.name = form.name.data.strip()
        variant.sku = form.sku.data.strip()
        variant.price_override = form.price_override.data
        variant.stock_quantity = form.stock_quantity.data

        # Handle image replacement
        if form.image.data:
            # Delete old image if it exists
            if variant.image_filename:
                old_path = os.path.join(
                    current_app.root_path, "static", variant.image_filename
                )
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(form.image.data.filename)
            upload_dir = os.path.join(
                current_app.root_path, "static", "uploads"
            )
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, filename)
            form.image.data.save(file_path)

            variant.image_filename = f"uploads/{filename}"

        db.session.commit()
        flash("Variant updated successfully", "success")

        return redirect(
            url_for(
                "admin.edit_product",
                product_id=variant.product_id,
            )
        )

    return render_template(
        "admin/product/variant_form.html",
        form=form,
        variant=variant,
        product=variant.product
    )


@admin_bp.route(
    "/variants/<int:variant_id>/delete",
    methods=["POST"],
)
def delete_variant(variant_id: int):
    variant = ProductVariant.query.filter_by(
        id=variant_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    product_id = variant.product_id
    db.session.delete(variant)
    db.session.commit()

    flash("Variant deleted", "success")
    return redirect(
        url_for(
            "admin.list_variants",
            product_id=product_id,
        )
    )

@admin_bp.route("/variants/<int:variant_id>/delete-image", methods=["POST"])
@login_required
@admin_required
def delete_variant_image(variant_id: int):
    variant = ProductVariant.query.filter_by(
        id=variant_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    if variant.image_filename:
        image_path = os.path.join(
            current_app.root_path, "static", variant.image_filename
        )
        if os.path.exists(image_path):
            os.remove(image_path)

        variant.image_filename = None
        db.session.commit()
        flash("Variant image removed", "success")

    return redirect(
        url_for("admin.edit_variant", variant_id=variant.id)
    )


@admin_bp.route(
    "/variants/<int:variant_id>/inventory",
    methods=["POST"],
)
@login_required
@admin_required
def update_inventory(variant_id: int):
    variant = ProductVariant.query.filter_by(
        id=variant_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    form = InventoryAdjustForm()

    if form.validate_on_submit():
        # Ensure stock never goes below zero
        new_stock = variant.stock_quantity + form.delta.data
        variant.stock_quantity = max(0, new_stock)

        db.session.commit()
        flash("Inventory updated", "success")

    else:
        flash("Invalid inventory input", "danger")

    return redirect(
        url_for("admin.edit_product", product_id=variant.product_id)
    )

