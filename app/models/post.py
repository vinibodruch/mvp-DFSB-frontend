"""Post model."""

from datetime import datetime

from app.extensions import db


class Post(db.Model):
    """Represents a user-authored post.

    Attributes:
        id: Primary key.
        title: Short descriptive title.
        content: Full text body of the post.
        user_id: Foreign key linking to the owning User.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp of the last update.
    """

    __tablename__ = "posts"

    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(200), nullable=False)
    content: str = db.Column(db.Text, nullable=False)
    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    created_at: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    author = db.relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post {self.id!r}: {self.title!r}>"
