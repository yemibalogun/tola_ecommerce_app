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

product_bp = Blueprint("admin_products", __name__, url_prefix="/admin/products")

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
        return redirect(url_for("admin_products.list_products"))
    
    form = ProductForm()

    # Load categories - adjust based on whether they should be tenant-scoped
    # If categories ARE tenant-scoped, filter by tenant_id
    categories = Category.query.order_by(Category.name.asc()).all()

    # Populate select field choices
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        image_path: Optional[str] = None

        # Handle image upload
        image_file: Optional[FileStorage] = form.image.data
        if image_file and image_file.filename:
            image_path = save_product_image(image_file)
        
        try:
            # Create product instance with validated form data
            product = Product()
            
            product.name = form.name.data.strip() if form.name.data else ""
            product.slug=form.slug.data.strip() if form.slug.data else unique_slug(Product, product.name)
            product.price=form.price.data # type: ignore
            product.description=form.description.data.strip() if form.description.data else None
            product.category_id=form.category_id.data or None
            product.is_active=form.is_active.data
            product.tenant_id=current_user.tenant_id
            product.image=image_path
            
            
            db.session.add(product)
            db.session.commit()

            flash("Product created successfully", "success")
            return redirect(url_for("admin_products.list_products"))
        
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

    form = ProductForm(obj=product)
    
    # Load categories - should match create_product logic
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        name_raw: Optional[str] = form.name.data
        if not name_raw:
            flash("Product name is required", "danger")
            return render_template(
                "admin/products/edit.html",
                form=form,
                product=product,
            )

        name: str = name_raw.strip()
        old_name: str = product.name

        try:
            product.name = name
            product.description = form.description.data.strip() if form.description.data else None
            product.price = form.price.data
            product.is_active = form.is_active.data
            product.category_id = form.category_id.data or None

            # Only regenerate slug if name actually changed
            if name != old_name:
                product.slug = unique_slug(Product, name)

            # Handle image upload
            image_file: Optional[FileStorage] = form.image.data
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
                flash("A product with this slug already exists. Please use a different name.", "danger")
            else:
                flash("Error updating product. Please check your input.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Unexpected error updating product: {str(e)}", "danger")

    return render_template(
        "admin/products/edit.html",
        form=form,
        product=product,
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

