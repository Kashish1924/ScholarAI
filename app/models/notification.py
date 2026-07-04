from app.extensions import db
from app.models.base import TimestampMixin


class Notification(TimestampMixin, db.Model):
    """Announcements, reminders, and important scholarship notices."""

    __tablename__ = "notifications"
    __table_args__ = (
        db.Index("ix_notifications_audience_active", "audience_type", "is_active"),
        db.Index("ix_notifications_window", "starts_at", "ends_at"),
    )

    notification_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False, default="general")
    audience_type = db.Column(db.String(30), nullable=False, default="all")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=True)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=True)
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

    created_by_admin = db.relationship("Admin", back_populates="created_notifications")
    related_scholarship = db.relationship("Scholarship", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification {self.title}>"
