import uuid
from flask import current_app, render_template, redirect, url_for, flash, request
from app.admin.forms import ProductVariantForm, InventoryAdjustForm
from flask_login import current_user, login_required
from app.admin import admin_bp
from app.admin.forms import ProductVariantForm, InventoryAdjustForm
from app.admin.decorators import admin_required
from app.extensions.db import db
from app.models.product import Product
from app.models.product_variant import ProductVariant
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from app.utils.uploads import save_product_image
from werkzeug.datastructures import FileStorage
import os 

@admin_bp.route("/products/<int:product_id>/variants")
@login_required
@admin_required
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
        "admin/products/variant_list.html",
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
            # Use default empty strings if data is None
            name = (form.name.data or "").strip()
            sku = (form.sku.data or "").strip()

            # Validate requred fields
            if not name or not sku:
                flash("Name and SKU are required", "danger")
                return render_template(
                    "admin/products/variant_form.html",
                    form=form,
                    product=product,
                )
            
            variant = ProductVariant()
            variant.product_id=product.id
            variant.tenant_id=current_user.tenant_id
            variant.name=name
            variant.sku=sku
            variant.price_override=form.price_override.data
            variant.stock_quantity=form.stock_quantity.data or 0

            # Handle image upload
            if form.image.data and form.image.data.filename:
                # Remove old image if exists
                if variant.image:
                    old_image_path = os.path.join(
                        current_app.root_path, 
                        "static", 
                        variant.image,
                    )
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                unique_name: str = f"{uuid.uuid4().hex}_{secure_filename(form.image.data.filename)}"

                upload_path = os.path.join(
                    current_app.root_path, 
                    'static', 
                    'uploads',
                )
                os.makedirs(upload_path, exist_ok=True)

                file_path: str = os.path.join(upload_path, unique_name)

                # Save new file
                form.image.data.save(file_path)

                # Store relative path in DB
                variant.image = f"uploads/{unique_name}"

            db.session.add(variant)
            db.session.commit()

            flash("Variant created", "success")
            return redirect(
                url_for(
                    "admin.list_variants",
                    product_id=product.id,
                )
            )
        except IntegrityError:
            db.session.rollback()
            flash("SKU already exists", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Unexpected error: {str(e)}", "danger")

    return render_template(
        "admin/products/variant_form.html",
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
        # Use default empty strings if data is None
        name = (form.name.data or "").strip()
        sku = (form.sku.data or "").strip()

        # Validate required fields
        if not name or not sku:
            flash("Name and SKU are required", "danger")
            return render_template(
                "admin/products/variant_form.html",
                form=form,
                variant=variant,
                product=variant.product
            )
        variant.name = name
        variant.sku = sku
        variant.price_override = form.price_override.data
        variant.stock_quantity = form.stock_quantity.data

        # Handle image replacement
        if form.image.data:
            # Delete old image if it exists
            if variant.image:
                old_path = os.path.join(
                    current_app.root_path, 
                    "static", 
                    variant.image,
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
        "admin/products/variant_form.html",
        form=form,
        variant=variant,
        product=variant.product
    )


@admin_bp.route(
    "/variants/<int:variant_id>/delete",
    methods=["POST"],
)
@login_required
@admin_required
def delete_variant(variant_id: int):
    variant = ProductVariant.query.filter_by(
        id=variant_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    product_id = variant.product_id

    try:
        db.session.delete(variant)
        db.session.commit()
        flash("Variant deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting variant: {str(e)}", "danger")

    return redirect(
        url_for(
            "admin.list_variants",
            product_id=product_id
        ))

@admin_bp.route("/variants/<int:variant_id>/delete-image", methods=["POST"])
@login_required
@admin_required
def delete_variant_image(variant_id: int):
    """Remove variant image from disk and database."""
    variant: ProductVariant = ProductVariant.query.filter_by(
        id=variant_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    if not variant.image:
        flash("No image to delete.", "warning")
        return redirect(
            url_for("admin.edit_variant", variant_id=variant.id)
        )

    try:
        image_path: str = os.path.join(
            current_app.root_path,
            "static",
            variant.image,
        )

        if os.path.exists(image_path):
            os.remove(image_path)

        variant.image = None
        db.session.commit()
        flash("Variant image removed successfully", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error removing image: {str(e)}", "danger")

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


@admin_bp.route("/<int:product_id>/variants", methods=["GET", "POST"])
@login_required
@admin_required
def manage_variants(product_id: int):
    """
    Create and list variants for a product.
    """

    # Ensure product belongs to current tenant
    product: Product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    form = ProductVariantForm()

    if form.validate_on_submit():
        try:
            # Validate name defensively
            name_raw: str | None = form.name.data
            if not name_raw:
                flash("Variant name is required", "danger")
                return redirect(request.url)

            # Handle optional image
            image_filename: str | None = None
            image_file: FileStorage | None = form.image.data

            if image_file and image_file.filename:
                image_filename = save_product_image(image_file)

            variant = ProductVariant()
            variant.product_id=product.id
            variant.tenant_id=current_user.tenant_id
            variant.name=name_raw.strip()
            variant.sku=form.sku.data.strip() if form.sku.data else ""
            variant.price_override=form.price_override.data
            stock_value: int = form.stock_quantity.data or 0

            variant.stock_quantity = stock_value
  
            variant.image=image_filename 
            

            db.session.add(variant)
            db.session.commit()

            flash("Variant added successfully", "success")
            return redirect(request.url)

        except IntegrityError:
            db.session.rollback()
            flash("SKU must be unique.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating variant: {str(e)}", "danger")

    variants = ProductVariant.query.filter_by(
        product_id=product.id,
        tenant_id=current_user.tenant_id,
    ).all()

    return render_template(
        "admin/products/manage_variants.html", 
        product=product,
        variants=variants,
        form=form,
    )
