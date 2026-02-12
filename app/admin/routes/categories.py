from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.extensions.db import db
from app.models.category import Category
from app.admin.forms import CategoryForm  # create this below
from slugify import slugify  # pip install python-slugify
from app.admin import admin_categories


@admin_categories.route("/")
@login_required
def list_categories():
    """
    Display all categories for the current tenant.
    """

    categories = (
        Category.query
        .filter_by(tenant_id=current_user.tenant_id)
        .order_by(Category.name.asc())
        .all()
    )

    return render_template(
        "admin/categories/list.html",
        categories=categories,
    )


@admin_categories.route("/create", methods=["GET", "POST"])
@login_required
def create_category():
    """
    Create a new category scoped to the current tenant.
    """

    form = CategoryForm()

    if form.validate_on_submit():
        raw_name: str | None = form.name.data

        # Defensive check for static typing + runtime safety
        if not raw_name:
            flash("Invalid category name.", "danger")
            return render_template("admin/categories/form.html", form=form)

        cleaned_name: str = raw_name.strip()

        # Prevent empty after strip
        if not cleaned_name:
            flash("Category name cannot be empty.", "danger")
            return render_template("admin/categories/form.html", form=form)


        # Generate slug safely
        generated_slug: str = slugify(cleaned_name)

        # Edge case: empty slug after sanitization
        if not generated_slug:
            flash("Invalid category name.", "danger")
            return render_template("admin/categories/form.html", form=form)
        
        category = Category()
        category.name=cleaned_name
        category.slug=generated_slug
        category.tenant_id=current_user.tenant_id
        
        db.session.add(category)

        try:
            db.session.commit()
            flash("Category created successfully.", "success")
            return redirect(url_for("admin_categories.list_categories"))

        except IntegrityError:
            # Slug conflict within same tenant
            db.session.rollback()
            flash("Category already exists.", "danger")

    return render_template("admin/categories/form.html", form=form)


@admin_categories.route("/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id: int):
    """
    Edit existing category.
    Enforces tenant isolation.
    """

    category = Category.query.filter_by(
        id=category_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    form = CategoryForm(obj=category)

    if form.validate_on_submit():

        raw_name: str | None = form.name.data

        if not raw_name:
            flash("Invalid category name.", "danger")
            return render_template("admin/categories/form.html", form=form)

        cleaned_name: str = raw_name.strip()

        if not cleaned_name:
            flash("Category name cannot be empty.", "danger")
            return render_template("admin/categories/form.html", form=form)

        category.name = cleaned_name
        category.slug = slugify(cleaned_name)


        try:
            db.session.commit()
            flash("Category updated successfully.", "success")
            return redirect(url_for("admin_categories.list_categories"))

        except IntegrityError:
            db.session.rollback()
            flash("Another category with this name exists.", "danger")

    return render_template("admin/categories/form.html", form=form)


@admin_categories.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id: int):
    """
    Delete a category.
    Prevent deletion if products are linked.
    """

    category = Category.query.filter_by(
        id=category_id,
        tenant_id=current_user.tenant_id,
    ).first_or_404()

    # Prevent deleting category if products exist
    if category.products:
        flash("Cannot delete category with existing products.", "danger")
        return redirect(url_for("admin_categories.list_categories"))

    db.session.delete(category)
    db.session.commit()

    flash("Category deleted successfully.", "success")
    return redirect(url_for("admin_categories.list_categories"))
