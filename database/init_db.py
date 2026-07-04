from app import create_app
from app.extensions import db
from app.models import (
    ActivityLog,
    Admin,
    Bookmark,
    Category,
    ContactMessage,
    FAQ,
    News,
    Notification,
    Scholarship,
    ScholarshipCategory,
    ScholarshipState,
    State,
    TrendingScholarship,
)


def initialize_database():
    """Create all configured database tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("ScholarAI database tables created successfully.")


if __name__ == "__main__":
    initialize_database()
