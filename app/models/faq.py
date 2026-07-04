from app.extensions import db
from app.models.base import TimestampMixin


class FAQ(TimestampMixin, db.Model):
    """Frequently asked questions managed by admins for student self-service."""

    __tablename__ = "faqs"
    __table_args__ = (
        db.Index("ix_faqs_published_order", "is_published", "display_order"),
    )

    faq_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, nullable=False, default=0)
    is_published = db.Column(db.Boolean, nullable=False, default=True)
    created_by_admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admins.admin_id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by_admin = db.relationship("Admin", back_populates="created_faqs")

    def __repr__(self) -> str:
        return f"<FAQ {self.question[:30]}>"
