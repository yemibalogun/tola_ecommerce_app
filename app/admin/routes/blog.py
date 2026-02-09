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
from app.web import web_blog_bp


@web_blog_bp.route("/blogs/create", methods=["GET", "POST"])
@login_required
def create_blog():
    if not current_user.tenant_id:
        abort(403)

    form = BlogForm()

    if form.validate_on_submit():
        try:
            title: str | None = form.title.data

            # Explicit guard - narrows Optional[str] -> str
            if not title:
                raise ValueError("Blog title is required")
            
            image_path = save_blog_image(form.image.data)

            blog = Blog()
            blog.title=form.title.data or ""
            blog.slug=generate_slug(title)
            blog.content=form.content.data or ""
            blog.image_path=image_path
            blog.tenant_id=current_user.tenant_id
            
            db.session.add(blog)
            db.session.commit()

            flash("Blog created successfully", "success")
            return redirect(url_for("blog.list_blogs"))

        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            flash(str(e), "danger")

    return render_template("blogs/create.html", form=form)

@web_blog_bp.route("/blogs")
def list_blogs():
    tenant_id = getattr(current_user, "tenant_id", None)

    if not tenant_id:
        blogs = []
    else:
        blogs = (
            Blog.query
            .filter_by(tenant_id=tenant_id)
            .order_by(Blog.created_at.desc())
            .all()
        )

    return render_template("blogs/list.html", blogs=blogs)
