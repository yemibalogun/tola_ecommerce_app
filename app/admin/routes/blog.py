# app/web/routes/blog.py
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions.db import db
from app.models.blog import Blog
from app.admin.forms import BlogForm
from app.utils.blog_utils import save_blog_image
from app.utils.slug import generate_unique_slug
from app.admin import admin_bp


@admin_bp.route("/blogs/create", methods=["GET", "POST"])
@login_required
def create_blog():
    if not current_user.tenant_id or not current_user.is_tenant_admin:
        abort(403)

    form = BlogForm()

    if form.validate_on_submit():
        try:
            title: str = form.title.data.strip() if form.title.data else ""
            image_path: str | None = None

            if form.image.data:
                image_path = save_blog_image(form.image.data)

            blog = Blog()
            blog.title=form.title.data or ""
            blog.slug = generate_unique_slug(title, current_user.tenant_id)
            blog.content=form.content.data or ""
            blog.image_path=image_path
            blog.tenant_id=current_user.tenant_id
            
            db.session.add(blog)
            db.session.commit()

            flash("Blog created successfully", "success")
            return redirect(url_for("web.list_blogs"))

        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            flash(str(e), "danger")

    return render_template("admin/blogs/create.html", form=form)

