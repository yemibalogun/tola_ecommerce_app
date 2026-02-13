from typing import List, Optional
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.admin.forms import ProductForm
from app.utils.slug import unique_slug
from app.extensions.db import db
from app.models.product import Product
from app.models.category import Category
from flask_login import current_user, login_required
from app.admin.decorators import admin_required
from sqlalchemy.exc import IntegrityError
import re
from app.utils.uploads import save_product_image
from werkzeug.datastructures import FileStorage
from app.admin import product_bp
from app.admin.forms import ProductVariantForm
from app.admin.forms import InventoryForm
from app.models.product_variant import ProductVariant



def slugify(name: str) -> str:
    """Generate a simple slug from a name."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

@product_bp.route("/", methods=["GET"])
@login_required
@admin_required
def list_products():
    """
    List all products for the current tenant.
    """
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template("admin/products/list.html", products=products)


@product_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_product():
    """Create a new product."""
    # Defensive check: admin must belong to a tenant
    if not current_user.tenant_id:
        flash("Tenant context missing", "danger")
        return redirect("admin/products/list.html")
    
    form = ProductForm()

    # Load categories - adjust based on whether they should be tenant-scoped
    # If categories ARE tenant-scoped, filter by tenant_id
    categories = Category.query.filter_by(
        tenant_id=current_user.tenant_id
        ).order_by(Category.name.asc()).all()
    
    # Defensive check - no categories exist
    if not categories:
        flash("Please create a category before adding products.", "warning")
        return redirect(url_for("admin_categories.create_category"))

    # Populate select field choices
    form.category_id.choices = [
        (c.id, c.name) for c in categories
    ]

    if form.validate_on_submit():
        image_path: Optional[str] = None

        # Handle image upload
        image_file: Optional[FileStorage] = form.image.data
        if image_file and image_file.filename:
            image_path = save_product_image(image_file)
        
        try:

            name: str = form.name.data.strip() if form.name.data else ""
            if not name:
                flash("Product name is required", "danger")
                return render_template(
                    "admin/products/create.html",
                    form=form,
                    categories=categories,
                )

            # Create product instance with validated form data
            product = Product()
          
            product.name = name
            product.slug=form.slug.data.strip() if form.slug.data else unique_slug(Product, name)
            product.price=form.price.data # type: ignore
            product.description=form.description.data.strip() if form.description.data else None
            product.category_id=form.category_id.data or None
            product.is_active=form.is_active.data
            product.tenant_id=current_user.tenant_id
            product.image=image_path
            
            
            db.session.add(product)
            db.session.commit()

            flash("Product created successfully", "success")
            return redirect(
                url_for(
                    "admin_products.manage_variants",
                    product_id=product.id
                )
            )

        except IntegrityError as e:
            db.session.rollback()
            # More specific error handling
            if "slug" in str(e.orig).lower():
                flash("A product with this slug already exists. Please use a different slug.", "danger")
            else:
                flash("Error creating product. Please check your input.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Unexpected error creating product: {str(e)}", "danger")

    return render_template(
        "admin/products/create.html",
        form=form,
        categories=categories,
    )



@product_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id: int):
    """Edit an existing product."""
    
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    # Main product form
    form = ProductForm(obj=product)

    # Inventory form pre-filled with current stock
    inventory_form = InventoryForm(stock_quantity=product.stock if hasattr(product, "stock") else 0)

    # Load categories
    categories = Category.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(Category.name.asc()).all()

    if not categories:
        flash("Please create a category before adding products.", "warning")
        return redirect(url_for("admin_categories.create_category"))

    form.category_id.choices = [(c.id, c.name) for c in categories]

    # Handle product update
    if form.validate_on_submit() and form.submit.data:
        name_raw = form.name.data
        if not name_raw:
            flash("Product name is required", "danger")
        else:
            name = name_raw.strip()
            old_name = product.name
            try:
                product.name = name
                product.description = form.description.data.strip() if form.description.data else None
                product.price = form.price.data
                product.is_active = form.is_active.data
                product.category_id = form.category_id.data or None

                if name != old_name:
                    product.slug = unique_slug(Product, name)

                # Handle image upload
                image_file = form.image.data
                if image_file and image_file.filename:
                    image_path = save_product_image(image_file)
                    if image_path:
                        product.image = image_path

                db.session.commit()
                flash("Product updated successfully", "success")
                return redirect(url_for("admin_products.list_products"))

            except IntegrityError as e:
                db.session.rollback()
                if "slug" in str(e.orig).lower():
                    flash("A product with this slug already exists.", "danger")
                else:
                    flash("Error updating product. Please check your input.", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Unexpected error updating product: {str(e)}", "danger")

    # Handle inventory update
    elif inventory_form.validate_on_submit() and inventory_form.submit.data:
        try:
            product.stock = inventory_form.stock.data
            db.session.commit()
            flash("Inventory updated successfully.", "success")
            return redirect(url_for("admin_products.edit_product", product_id=product.id))
        except Exception:
            db.session.rollback()
            flash("Error updating inventory.", "danger")

    return render_template(
        "admin/products/edit.html",
        form=form,
        inventory_form=inventory_form,
        product=product
    )



@product_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_product(product_id: int):
    """Delete a product."""
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    try:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting product: {str(e)}", "danger")
    
    return redirect(url_for("admin_products.list_products"))


@product_bp.route("/<int:product_id>/variants", methods=["GET", "POST"])
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
        url_for("admin_products.manage_variants", product_id=product.id),
        product=product,
        variants=variants,
        form=form,
    )
