from datetime import date

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import Admin, Scholarship
from app.utils.validation import ValidationError


class AdminService:
    """Authentication and dashboard operations for admin users."""

    @staticmethod
    def authenticate_admin(email: str, password: str) -> Admin | None:
        """Return the authenticated admin or None."""
        admin = Admin.query.filter_by(email=email.strip().lower(), is_active=True).first()
        if admin is None:
            return None
        if not check_password_hash(admin.password_hash, password):
            return None
        return admin

    @staticmethod
    def create_admin(full_name: str, email: str, password: str) -> Admin:
        """Create a new admin with a hashed password."""
        normalized_email = email.strip().lower()
        if Admin.query.filter_by(email=normalized_email).first():
            raise ValidationError({"email": ["An admin with this email already exists."]})

        admin = Admin(
            full_name=full_name.strip(),
            email=normalized_email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(admin)
        db.session.commit()
        return admin

    @staticmethod
    def get_admin_by_id(admin_id: int) -> Admin | None:
        """Return admin by id."""
        return Admin.query.filter_by(admin_id=admin_id, is_active=True).first()

    @staticmethod
    def get_dashboard_summary() -> dict:
        """Return lightweight dashboard analytics."""
        total_scholarships = Scholarship.query.count()
        government_count = Scholarship.query.filter_by(scholarship_type="government").count()
        private_count = Scholarship.query.filter_by(scholarship_type="private").count()
        published_count = Scholarship.query.filter_by(status="published").count()
        featured_count = Scholarship.query.filter_by(is_featured=True).count()

        recent_scholarships = (
            Scholarship.query.order_by(Scholarship.created_at.desc()).limit(5).all()
        )
        deadline_watch = (
            Scholarship.query.filter(
                Scholarship.status == "published",
                Scholarship.application_end_date >= date.today(),
            )
            .order_by(Scholarship.application_end_date.asc())
            .limit(5)
            .all()
        )

        return {
            "totals": {
                "total_scholarships": total_scholarships,
                "government_scholarships": government_count,
                "private_scholarships": private_count,
                "published_scholarships": published_count,
                "featured_scholarships": featured_count,
            },
            "recent_scholarships": recent_scholarships,
            "deadline_watch": deadline_watch,
        }
