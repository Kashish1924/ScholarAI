from app.extensions import db
from app.models.base import TimestampMixin


class News(TimestampMixin, db.Model):
    """News articles and scholarship updates displayed to students."""

    __tablename__ = "news"
    __table_args__ = (
        db.Index("ix_news_published_priority", "is_published", "priority", "published_at"),
    )

    news_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    summary = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    priority = db.Column(db.Integer, nullable=False, default=0)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_by_admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admins.admin_id", ondelete="SET NULL"),
        nullable=True,
    )
    related_scholarship_id = db.Column(
        db.Integer,
        db.ForeignKey("scholarships.scholarship_id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by_admin = db.relationship("Admin", back_populates="created_news")
    related_scholarship = db.relationship("Scholarship", back_populates="related_news")

    def __repr__(self) -> str:
        return f"<News {self.title}>"
