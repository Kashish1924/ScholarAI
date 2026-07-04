from app.extensions import db
from app.models.base import TimestampMixin


class Admin(TimestampMixin, db.Model):
    """Administrative users who manage the platform."""

    __tablename__ = "admins"
    __table_args__ = (
        db.Index("ix_admins_email_active", "email", "is_active"),
    )

    admin_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    activity_logs = db.relationship("ActivityLog", back_populates="admin", lazy="dynamic")
    contact_resolutions = db.relationship(
        "ContactMessage",
        back_populates="resolved_by_admin",
        lazy="dynamic",
        foreign_keys="ContactMessage.resolved_by_admin_id",
    )
    created_faqs = db.relationship("FAQ", back_populates="created_by_admin", lazy="dynamic")
    created_news = db.relationship("News", back_populates="created_by_admin", lazy="dynamic")
    created_notifications = db.relationship(
        "Notification",
        back_populates="created_by_admin",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Admin {self.email}>"
