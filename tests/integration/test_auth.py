"""Integration tests for authentication routes."""

import pytest


def _register(client, username="alice", email="alice@example.com", password="securepass1",
              follow_redirects=True):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=follow_redirects,
    )


def _login(client, email="alice@example.com", password="securepass1"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def _logout(client):
    client.post("/auth/logout", follow_redirects=True)


class TestRegistration:
    def test_register_page_loads(self, client):
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data

    def test_register_success(self, client, db):
        response = _register(client)
        assert response.status_code == 200
        assert b"Dashboard" in response.data or b"dashboard" in response.data.lower()

    def test_register_duplicate_email(self, client, db):
        # Register alice then log out so we can attempt duplicate registration
        _register(client, follow_redirects=False)
        _logout(client)
        response = _register(client, username="bob")
        assert b"already registered" in response.data

    def test_register_duplicate_username(self, client, db):
        _register(client, follow_redirects=False)
        _logout(client)
        response = _register(client, email="bob@example.com")
        assert b"already taken" in response.data

    def test_register_password_mismatch(self, client, db):
        response = client.post(
            "/auth/register",
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password": "securepass1",
                "confirm_password": "differentpass",
            },
            follow_redirects=True,
        )
        assert b"Passwords must match" in response.data


class TestLogin:
    def test_login_page_loads(self, client):
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_login_success(self, client, db):
        _register(client, follow_redirects=False)
        _logout(client)
        response = _login(client)
        assert response.status_code == 200
        assert b"Logged in" in response.data or b"dashboard" in response.data.lower()

    def test_login_wrong_password(self, client, db):
        _register(client, follow_redirects=False)
        _logout(client)
        response = _login(client, password="wrongpassword")
        assert b"Invalid email or password" in response.data

    def test_login_unknown_email(self, client, db):
        response = _login(client, email="nobody@example.com")
        assert b"Invalid email or password" in response.data


class TestLogout:
    def test_logout_requires_login(self, client):
        response = client.post("/auth/logout", follow_redirects=True)
        assert response.status_code == 200

    def test_logout_success(self, client, db):
        _register(client)
        response = client.post("/auth/logout", follow_redirects=True)
        assert response.status_code == 200
