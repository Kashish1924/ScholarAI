from app.extensions import db
from app.models.base import TimestampMixin


class ActivityLog(TimestampMixin, db.Model):
    """Admin audit trail for sensitive actions across the platform."""

    __tablename__ = "activity_logs"
    __table_args__ = (
        db.Index("ix_activity_logs_admin_action", "admin_id", "action_type"),
        db.Index("ix_activity_logs_entity", "entity_type", "entity_id"),
    )

    log_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admins.admin_id", ondelete="SET NULL"),
        nullable=True,
    )
    action_type = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)

    admin = db.relationship("Admin", back_populates="activity_logs")

    def __repr__(self) -> str:
        return f"<ActivityLog {self.action_type}>"
