"""User model."""

from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    """Represents an application user.

    Attributes:
        id: Primary key.
        username: Unique display name.
        email: Unique email address (used for login).
        password_hash: Bcrypt-hashed password — never stored in plaintext.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp of the last update.
    """

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(
        db.String(64), unique=True, nullable=False, index=True
    )
    email: str = db.Column(
        db.String(120), unique=True, nullable=False, index=True
    )
    password_hash: str = db.Column(db.String(128), nullable=False)
    created_at: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    posts = db.relationship("Post", back_populates="author", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.username!r}>"
