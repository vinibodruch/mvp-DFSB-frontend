"""Authentication service — business logic for registration and login.

This module must *not* import any Flask request/response objects.
All HTTP concerns belong in the controller layer.
"""

import logging

from app.extensions import bcrypt
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyTakenError,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Handles user registration and authentication business logic.

    Args:
        user_repo: The :class:`~app.repositories.user_repository.UserRepository`
                   to use for data access.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    def register(self, username: str, email: str, password: str) -> User:
        """Register a new user.

        Args:
            username: Desired display name.
            email: Email address to register.
            password: Plaintext password (will be hashed before storage).

        Returns:
            The newly created :class:`~app.models.user.User`.

        Raises:
            EmailAlreadyRegisteredError: If the email is taken.
            UsernameAlreadyTakenError: If the username is taken.
        """
        if self._user_repo.email_exists(email):
            raise EmailAlreadyRegisteredError(
                f"Email already registered: {email}"
            )
        if self._user_repo.username_exists(username):
            raise UsernameAlreadyTakenError(
                f"Username already taken: {username}"
            )

        password_hash: str = bcrypt.generate_password_hash(password).decode(
            "utf-8"
        )
        user = self._user_repo.create(
            username=username, email=email, password_hash=password_hash
        )
        logger.info("New user registered: id=%s username=%s", user.id, username)
        return user

    def authenticate(self, email: str, password: str) -> User:
        """Authenticate a user by email and password.

        Args:
            email: The user's email address.
            password: Plaintext password to verify.

        Returns:
            The authenticated :class:`~app.models.user.User`.

        Raises:
            InvalidCredentialsError: If the credentials are incorrect.
        """
        user = self._user_repo.get_by_email(email)
        if user is None or not bcrypt.check_password_hash(
            user.password_hash, password
        ):
            logger.warning(
                "Failed login attempt for email: %s", email
            )
            raise InvalidCredentialsError("Invalid email or password.")

        logger.info("User authenticated: id=%s username=%s", user.id, user.username)
        return user
