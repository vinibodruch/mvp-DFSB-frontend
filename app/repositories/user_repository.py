"""User repository — all database queries for the User model."""

from app.extensions import db
from app.models.user import User


class UserRepository:
    """Data-access layer for :class:`~app.models.user.User`.

    All SQLAlchemy queries related to users must live here.
    Controllers and services must never query the DB directly.
    """

    def get_by_id(self, user_id: int) -> User | None:
        """Return the user with the given primary key, or ``None``."""
        return db.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email address, or ``None``."""
        return User.query.filter_by(email=email).first()

    def get_by_username(self, username: str) -> User | None:
        """Return the user with the given username, or ``None``."""
        return User.query.filter_by(username=username).first()

    def email_exists(self, email: str) -> bool:
        """Return ``True`` if the email is already registered."""
        return self.get_by_email(email) is not None

    def username_exists(self, username: str) -> bool:
        """Return ``True`` if the username is already taken."""
        return self.get_by_username(username) is not None

    def create(self, username: str, email: str, password_hash: str) -> User:
        """Persist a new User and return it.

        Args:
            username: Display name (must be unique).
            email: Email address (must be unique).
            password_hash: Pre-hashed password string.

        Returns:
            The newly created :class:`~app.models.user.User` instance.
        """
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user
