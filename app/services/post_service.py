"""Post service — business logic for post management.

This module must *not* import any Flask request/response objects.
"""

import logging

from app.models.post import Post
from app.models.user import User
from app.repositories.post_repository import PostRepository
from app.services.exceptions import PostNotFoundError, UnauthorizedPostAccessError

logger = logging.getLogger(__name__)


class PostService:
    """Handles CRUD business logic for posts.

    Args:
        post_repo: The :class:`~app.repositories.post_repository.PostRepository`
                   to use for data access.
    """

    def __init__(self, post_repo: PostRepository) -> None:
        self._post_repo = post_repo

    def get_all_paginated(self, page: int = 1, per_page: int = 10):
        """Return paginated posts (newest first).

        Args:
            page: Page number (1-indexed).
            per_page: Records per page.

        Returns:
            A SQLAlchemy :class:`Pagination` object.
        """
        return self._post_repo.get_all_paginated(page=page, per_page=per_page)

    def get_by_user_paginated(
        self, user_id: int, page: int = 1, per_page: int = 10
    ):
        """Return paginated posts for a specific user.

        Args:
            user_id: Owner's primary key.
            page: Page number.
            per_page: Records per page.

        Returns:
            A SQLAlchemy :class:`Pagination` object.
        """
        return self._post_repo.get_by_user_paginated(
            user_id=user_id, page=page, per_page=per_page
        )

    def get_post(self, post_id: int) -> Post:
        """Return a single post by ID.

        Args:
            post_id: The post's primary key.

        Returns:
            The :class:`~app.models.post.Post` instance.

        Raises:
            PostNotFoundError: If no post exists with that ID.
        """
        post = self._post_repo.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(f"Post not found: id={post_id}")
        return post

    def create_post(self, title: str, content: str, author: User) -> Post:
        """Create a new post owned by *author*.

        Args:
            title: Post title.
            content: Post body.
            author: The currently logged-in user.

        Returns:
            The newly created :class:`~app.models.post.Post`.
        """
        post = self._post_repo.create(
            title=title, content=content, user_id=author.id
        )
        logger.info(
            "Post created: id=%s by user_id=%s", post.id, author.id
        )
        return post

    def update_post(
        self, post_id: int, title: str, content: str, requester: User
    ) -> Post:
        """Update a post if *requester* is its owner.

        Args:
            post_id: Primary key of the post to update.
            title: New title.
            content: New body.
            requester: The user attempting the update.

        Returns:
            The updated :class:`~app.models.post.Post`.

        Raises:
            PostNotFoundError: If the post does not exist.
            UnauthorizedPostAccessError: If the requester doesn't own the post.
        """
        post = self.get_post(post_id)
        self._assert_owns_post(post, requester)
        updated = self._post_repo.update(post, title=title, content=content)
        logger.info(
            "Post updated: id=%s by user_id=%s", post_id, requester.id
        )
        return updated

    def delete_post(self, post_id: int, requester: User) -> None:
        """Delete a post if *requester* is its owner.

        Args:
            post_id: Primary key of the post to delete.
            requester: The user attempting the deletion.

        Raises:
            PostNotFoundError: If the post does not exist.
            UnauthorizedPostAccessError: If the requester doesn't own the post.
        """
        post = self.get_post(post_id)
        self._assert_owns_post(post, requester)
        self._post_repo.delete(post)
        logger.info(
            "Post deleted: id=%s by user_id=%s", post_id, requester.id
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _assert_owns_post(self, post: Post, requester: User) -> None:
        """Raise :exc:`UnauthorizedPostAccessError` if *requester* != owner."""
        if post.user_id != requester.id:
            raise UnauthorizedPostAccessError(
                f"User {requester.id} does not own post {post.id}."
            )
