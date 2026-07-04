from app.extensions import db
from app.models.base import TimestampMixin


class Bookmark(TimestampMixin, db.Model):
    """Browser-session bookmarks for students who do not need accounts."""

    __tablename__ = "bookmarks"
    __table_args__ = (
        db.UniqueConstraint(
            "browser_session_key",
            "scholarship_id",
            name="uq_bookmarks_session_scholarship",
        ),
        db.Index("ix_bookmarks_session_created", "browser_session_key", "created_at"),
    )

    bookmark_id = db.Column(db.Integer, primary_key=True)
    browser_session_key = db.Column(db.String(120), nullable=False, index=True)
    scholarship_id = db.Column(
        db.Integer,
        db.ForeignKey("scholarships.scholarship_id", ondelete="CASCADE"),
        nullable=False,
    )

    scholarship = db.relationship("Scholarship", back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<Bookmark {self.browser_session_key}:{self.scholarship_id}>"
