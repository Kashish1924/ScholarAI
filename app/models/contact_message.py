from app.extensions import db
from app.models.base import TimestampMixin


class ContactMessage(TimestampMixin, db.Model):
    """Messages sent from the public contact form for admin follow-up."""

    __tablename__ = "contact_messages"
    __table_args__ = (
        db.Index("ix_contact_messages_resolution", "is_resolved", "created_at"),
        db.Index("ix_contact_messages_email", "email"),
    )

    message_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, nullable=False, default=False)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    resolved_by_admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admins.admin_id", ondelete="SET NULL"),
        nullable=True,
    )

    resolved_by_admin = db.relationship(
        "Admin",
        back_populates="contact_resolutions",
        foreign_keys=[resolved_by_admin_id],
    )

    def __repr__(self) -> str:
        return f"<ContactMessage {self.email}>"
