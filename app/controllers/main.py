"""Main blueprint — public-facing pages (index, dashboard)."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.repositories.post_repository import PostRepository
from app.services.post_service import PostService

main_bp = Blueprint("main", __name__)

_post_repo = PostRepository()
_post_service = PostService(_post_repo)


@main_bp.route("/")
def index():
    """Public landing / index page."""
    page = 1
    pagination = _post_service.get_all_paginated(page=page, per_page=5)
    return render_template("main/index.html", pagination=pagination)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Authenticated user dashboard showing their own posts."""
    page = 1
    pagination = _post_service.get_by_user_paginated(
        user_id=current_user.id, page=page, per_page=10
    )
    return render_template("main/dashboard.html", pagination=pagination)
