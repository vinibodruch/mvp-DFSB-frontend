"""Integration tests for posts routes."""

import pytest


def _register_and_login(client, username="alice", email="alice@example.com"):
    client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": "securepass1",
            "confirm_password": "securepass1",
        },
        follow_redirects=True,
    )


def _create_post(client, title="Hello World", content="This is a test post with enough content."):
    return client.post(
        "/posts/new",
        data={"title": title, "content": content},
        follow_redirects=True,
    )


class TestPostList:
    def test_list_page_loads(self, client):
        response = client.get("/posts/")
        assert response.status_code == 200
        assert b"Posts" in response.data


class TestPostCreate:
    def test_create_requires_login(self, client):
        response = client.get("/posts/new", follow_redirects=True)
        assert response.status_code == 200
        assert b"log in" in response.data.lower() or b"login" in response.data.lower()

    def test_create_success(self, client, db):
        _register_and_login(client)
        response = _create_post(client)
        assert response.status_code == 200
        assert b"Hello World" in response.data

    def test_create_invalid_short_content(self, client, db):
        _register_and_login(client)
        response = _create_post(client, content="short")
        assert response.status_code == 200
        assert b"Field must be at least" in response.data or b"too short" in response.data.lower()


class TestPostView:
    def test_view_nonexistent_post_404(self, client):
        response = client.get("/posts/99999")
        assert response.status_code == 404

    def test_view_post_success(self, client, db):
        _register_and_login(client)
        _create_post(client)
        response = client.get("/posts/1")
        assert response.status_code == 200
        assert b"Hello World" in response.data


class TestPostEdit:
    def test_edit_requires_login(self, client, db):
        _register_and_login(client)
        _create_post(client)
        with client.session_transaction() as sess:
            sess.clear()
        response = client.get("/posts/1/edit", follow_redirects=True)
        assert response.status_code == 200

    def test_edit_own_post(self, client, db):
        _register_and_login(client)
        _create_post(client)
        response = client.post(
            "/posts/1/edit",
            data={"title": "Updated Title", "content": "Updated content that is long enough."},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Updated Title" in response.data

    def test_edit_other_user_post_403(self, client, db):
        _register_and_login(client, username="alice", email="alice@example.com")
        _create_post(client)
        # Log out and in as bob
        client.post("/auth/logout")
        _register_and_login(client, username="bob", email="bob@example.com")
        response = client.post(
            "/posts/1/edit",
            data={"title": "Hack", "content": "Hacked content here please ignore."},
            follow_redirects=True,
        )
        assert response.status_code == 403


class TestPostDelete:
    def test_delete_own_post(self, client, db):
        _register_and_login(client)
        _create_post(client)
        response = client.post("/posts/1/delete", follow_redirects=True)
        assert response.status_code == 200
        assert b"deleted" in response.data.lower()

    def test_delete_other_user_post_403(self, client, db):
        _register_and_login(client, username="alice", email="alice@example.com")
        _create_post(client)
        client.post("/auth/logout")
        _register_and_login(client, username="bob", email="bob@example.com")
        response = client.post("/posts/1/delete", follow_redirects=True)
        assert response.status_code == 403
