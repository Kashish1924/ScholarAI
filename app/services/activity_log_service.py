import json

from flask import request

from app.extensions import db
from app.models import ActivityLog


class ActivityLogService:
    """Service for recording admin activity logs."""

    @staticmethod
    def log_admin_activity(
        admin_id: int | None,
        action_type: str,
        entity_type: str,
        description: str,
        entity_id: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Persist an admin activity log entry."""
        metadata_json = json.dumps(metadata) if metadata else None
        log = ActivityLog(
            admin_id=admin_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=request.user_agent.string if request.user_agent else None,
            metadata_json=metadata_json,
        )
        db.session.add(log)
        db.session.commit()
