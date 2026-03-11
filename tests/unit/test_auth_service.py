"""Unit tests for AuthService."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.auth_service import AuthService
from app.services.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyTakenError,
)


def _make_service(email_exists=False, username_exists=False, user=None):
    """Create an AuthService with a mocked UserRepository."""
    repo = MagicMock()
    repo.email_exists.return_value = email_exists
    repo.username_exists.return_value = username_exists
    repo.get_by_email.return_value = user
    repo.create.return_value = MagicMock(id=1, username="alice")
    return AuthService(repo)


class TestRegister:
    """Tests for AuthService.register."""

    def test_register_success(self, app):
        """Happy path: valid credentials create a user."""
        with app.app_context():
            service = _make_service()
            user = service.register("alice", "alice@example.com", "securepass1")
            assert user is not None

    def test_register_duplicate_email_raises(self, app):
        """Duplicate email raises EmailAlreadyRegisteredError."""
        with app.app_context():
            service = _make_service(email_exists=True)
            with pytest.raises(EmailAlreadyRegisteredError):
                service.register("alice", "alice@example.com", "securepass1")

    def test_register_duplicate_username_raises(self, app):
        """Duplicate username raises UsernameAlreadyTakenError."""
        with app.app_context():
            service = _make_service(username_exists=True)
            with pytest.raises(UsernameAlreadyTakenError):
                service.register("alice", "alice@example.com", "securepass1")


class TestAuthenticate:
    """Tests for AuthService.authenticate."""

    def test_authenticate_invalid_email_raises(self, app):
        """Unknown email raises InvalidCredentialsError."""
        with app.app_context():
            service = _make_service(user=None)
            with pytest.raises(InvalidCredentialsError):
                service.authenticate("nobody@example.com", "password")

    def test_authenticate_wrong_password_raises(self, app):
        """Wrong password raises InvalidCredentialsError."""
        with app.app_context():
            fake_user = MagicMock()
            fake_user.password_hash = "hashed"
            service = _make_service(user=fake_user)

            with patch(
                "app.services.auth_service.bcrypt.check_password_hash",
                return_value=False,
            ):
                with pytest.raises(InvalidCredentialsError):
                    service.authenticate("alice@example.com", "wrongpass")

    def test_authenticate_success(self, app):
        """Correct credentials return the user object."""
        with app.app_context():
            fake_user = MagicMock()
            fake_user.password_hash = "hashed"
            service = _make_service(user=fake_user)

            with patch(
                "app.services.auth_service.bcrypt.check_password_hash",
                return_value=True,
            ):
                result = service.authenticate("alice@example.com", "goodpass")
                assert result is fake_user
