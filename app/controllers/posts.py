"""Posts blueprint — CRUD for blog posts."""

import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.repositories.post_repository import PostRepository
from app.services.exceptions import PostNotFoundError, UnauthorizedPostAccessError
from app.services.post_service import PostService

logger = logging.getLogger(__name__)

posts_bp = Blueprint("posts", __name__)

_post_repo = PostRepository()
_post_service = PostService(_post_repo)


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------


class PostForm(FlaskForm):
    """WTForms form for creating and editing posts."""

    title = StringField(
        "Title", validators=[DataRequired(), Length(min=3, max=200)]
    )
    content = TextAreaField(
        "Content", validators=[DataRequired(), Length(min=10)]
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@posts_bp.route("/")
def list_posts():
    """List all posts with pagination."""
    page = request.args.get("page", 1, type=int)
    pagination = _post_service.get_all_paginated(page=page, per_page=10)
    return render_template("posts/list.html", pagination=pagination)


@posts_bp.route("/<int:post_id>")
def view_post(post_id: int):
    """Display a single post."""
    try:
        post = _post_service.get_post(post_id)
    except PostNotFoundError:
        abort(404)
    return render_template("posts/view.html", post=post)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_post():
    """Create a new post."""
    form = PostForm()
    if form.validate_on_submit():
        post = _post_service.create_post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
        )
        flash("Post created successfully.", "success")
        return redirect(url_for("posts.view_post", post_id=post.id))
    return render_template("posts/form.html", form=form, action="Create")


@posts_bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
    """Edit an existing post (owner only)."""
    try:
        post = _post_service.get_post(post_id)
    except PostNotFoundError:
        abort(404)

    if post.user_id != current_user.id:
        abort(403)

    form = PostForm(obj=post)
    if form.validate_on_submit():
        try:
            _post_service.update_post(
                post_id=post_id,
                title=form.title.data,
                content=form.content.data,
                requester=current_user,
            )
            flash("Post updated.", "success")
            return redirect(url_for("posts.view_post", post_id=post_id))
        except UnauthorizedPostAccessError:
            abort(403)

    return render_template("posts/form.html", form=form, action="Edit", post=post)


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    """Delete a post (owner only)."""
    try:
        _post_service.delete_post(post_id=post_id, requester=current_user)
        flash("Post deleted.", "info")
    except PostNotFoundError:
        abort(404)
    except UnauthorizedPostAccessError:
        abort(403)
    return redirect(url_for("posts.list_posts"))
