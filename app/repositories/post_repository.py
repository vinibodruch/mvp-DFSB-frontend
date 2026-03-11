"""Post repository — all database queries for the Post model."""

from app.extensions import db
from app.models.post import Post


class PostRepository:
    """Data-access layer for :class:`~app.models.post.Post`.

    All SQLAlchemy queries related to posts must live here.
    """

    def get_by_id(self, post_id: int) -> Post | None:
        """Return the post with the given primary key, or ``None``."""
        return db.session.get(Post, post_id)

    def get_all_paginated(self, page: int = 1, per_page: int = 10):
        """Return a SQLAlchemy pagination object for all posts.

        Args:
            page: The page number (1-indexed).
            per_page: Number of records per page.

        Returns:
            A :class:`flask_sqlalchemy.Pagination` object.
        """
        return (
            Post.query.order_by(Post.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        )

    def get_by_user_paginated(
        self, user_id: int, page: int = 1, per_page: int = 10
    ):
        """Return paginated posts belonging to a specific user.

        Args:
            user_id: Owner's primary key.
            page: The page number.
            per_page: Records per page.

        Returns:
            A :class:`flask_sqlalchemy.Pagination` object.
        """
        return (
            Post.query.filter_by(user_id=user_id)
            .order_by(Post.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def create(self, title: str, content: str, user_id: int) -> Post:
        """Persist a new Post and return it.

        Args:
            title: Post title.
            content: Post body text.
            user_id: Primary key of the owning user.

        Returns:
            The newly created :class:`~app.models.post.Post` instance.
        """
        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        return post

    def update(self, post: Post, title: str, content: str) -> Post:
        """Update an existing post's title and content.

        Args:
            post: The post instance to update.
            title: New title.
            content: New body text.

        Returns:
            The updated :class:`~app.models.post.Post` instance.
        """
        post.title = title
        post.content = content
        db.session.commit()
        return post

    def delete(self, post: Post) -> None:
        """Delete a post from the database.

        Args:
            post: The post instance to remove.
        """
        db.session.delete(post)
        db.session.commit()
