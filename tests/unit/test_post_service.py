"""Unit tests for PostService."""

from unittest.mock import MagicMock

import pytest

from app.services.exceptions import PostNotFoundError, UnauthorizedPostAccessError
from app.services.post_service import PostService


def _make_post(post_id: int, user_id: int):
    post = MagicMock()
    post.id = post_id
    post.user_id = user_id
    post.title = "Old title"
    post.content = "Old content"
    return post


def _make_user(user_id: int):
    user = MagicMock()
    user.id = user_id
    return user


def _make_service(post=None):
    repo = MagicMock()
    repo.get_by_id.return_value = post
    return PostService(repo)


class TestGetPost:
    def test_raises_when_not_found(self):
        service = _make_service(post=None)
        with pytest.raises(PostNotFoundError):
            service.get_post(999)

    def test_returns_post_when_found(self):
        post = _make_post(1, 1)
        service = _make_service(post=post)
        result = service.get_post(1)
        assert result is post


class TestUpdatePost:
    def test_raises_when_not_owner(self):
        post = _make_post(1, user_id=1)
        requester = _make_user(user_id=2)
        service = _make_service(post=post)
        with pytest.raises(UnauthorizedPostAccessError):
            service.update_post(1, "title", "content", requester)

    def test_updates_when_owner(self):
        post = _make_post(1, user_id=1)
        requester = _make_user(user_id=1)
        updated = _make_post(1, user_id=1)
        repo = MagicMock()
        repo.get_by_id.return_value = post
        repo.update.return_value = updated
        service = PostService(repo)

        result = service.update_post(1, "New title", "New content", requester)
        repo.update.assert_called_once_with(post, title="New title", content="New content")
        assert result is updated


class TestDeletePost:
    def test_raises_when_not_found(self):
        service = _make_service(post=None)
        with pytest.raises(PostNotFoundError):
            service.delete_post(999, _make_user(1))

    def test_raises_when_not_owner(self):
        post = _make_post(1, user_id=1)
        service = _make_service(post=post)
        with pytest.raises(UnauthorizedPostAccessError):
            service.delete_post(1, _make_user(user_id=2))

    def test_deletes_when_owner(self):
        post = _make_post(1, user_id=1)
        requester = _make_user(user_id=1)
        repo = MagicMock()
        repo.get_by_id.return_value = post
        service = PostService(repo)
        service.delete_post(1, requester)
        repo.delete.assert_called_once_with(post)
