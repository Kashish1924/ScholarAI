from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Admin, Category, FAQ, News, Notification, Scholarship, State
from app.services.content_service import ContentService
from app.services.scholarship_service import ScholarshipService


CATEGORY_SEEDS = [
    ("General", "general", "Open scholarship category."),
    ("OBC", "obc", "Other Backward Class scholarships."),
    ("SC", "sc", "Scheduled Caste scholarships."),
    ("ST", "st", "Scheduled Tribe scholarships."),
    ("EWS", "ews", "Economically weaker section scholarships."),
    ("Minority", "minority", "Minority community scholarships."),
    ("Merit", "merit", "Merit-based scholarship opportunities."),
]

STATE_SEEDS = [
    ("Delhi", "DL", True),
    ("Maharashtra", "MH", False),
    ("Karnataka", "KA", False),
    ("Tamil Nadu", "TN", False),
    ("Uttar Pradesh", "UP", False),
    ("West Bengal", "WB", False),
    ("Telangana", "TS", False),
    ("Gujarat", "GJ", False),
]

SAMPLE_SCHOLARSHIPS = [
    {
        "scholarship_name": "AICTE Pragati Scholarship",
        "provider_name": "AICTE",
        "scholarship_type": "government",
        "scholarship_amount": "50000",
        "eligibility_description": "Support for meritorious girl students pursuing technical education.",
        "minimum_cgpa": "7.0",
        "maximum_family_income": "800000",
        "gender": "female",
        "degree": "B.Tech",
        "branch": "all",
        "academic_year": "all",
        "minority_eligibility": False,
        "disability_eligibility": False,
        "hosteller_eligibility": False,
        "day_scholar_eligibility": False,
        "required_documents": "Aadhaar, income certificate, admission proof, bank passbook",
        "application_link": "https://example.org/aicte-pragati/apply",
        "official_website": "https://example.org/aicte-pragati",
        "application_start_date": "2026-07-01",
        "application_end_date": "2026-09-15",
        "status": "published",
        "is_featured": True,
        "trending_score": 95,
        "description": "A flagship scholarship for female B.Tech students needing tuition support.",
        "benefits": "Tuition assistance and academic support.",
        "selection_process": "Document verification and merit ranking.",
        "is_renewable": True,
        "categories": ["general", "obc", "sc", "st", "ews"],
        "states": ["DL", "MH", "KA", "TN", "UP"],
    },
    {
        "scholarship_name": "National Merit Support Scheme",
        "provider_name": "Ministry of Education",
        "scholarship_type": "government",
        "scholarship_amount": "60000",
        "eligibility_description": "Scholarship for high-performing B.Tech students from low-income families.",
        "minimum_cgpa": "8.0",
        "maximum_family_income": "300000",
        "gender": "all",
        "degree": "B.Tech",
        "branch": "CSE",
        "academic_year": "3",
        "minority_eligibility": False,
        "disability_eligibility": False,
        "hosteller_eligibility": False,
        "day_scholar_eligibility": False,
        "required_documents": "Income certificate, marksheets, ID proof",
        "application_link": "https://example.org/national-merit/apply",
        "official_website": "https://example.org/national-merit",
        "application_start_date": "2026-06-20",
        "application_end_date": "2026-08-20",
        "status": "published",
        "is_featured": True,
        "trending_score": 90,
        "description": "A merit-first scholarship for academically strong third-year CSE students.",
        "benefits": "Direct financial support and recognition certificate.",
        "selection_process": "Merit shortlist followed by document review.",
        "is_renewable": False,
        "categories": ["obc", "ews", "merit"],
        "states": ["DL", "TS", "KA"],
    },
    {
        "scholarship_name": "Private Tech Excellence Grant",
        "provider_name": "Future Engineers Foundation",
        "scholarship_type": "private",
        "scholarship_amount": "40000",
        "eligibility_description": "Private scholarship for engineering students with strong academics and project work.",
        "minimum_cgpa": "7.5",
        "maximum_family_income": "600000",
        "gender": "all",
        "degree": "B.Tech",
        "branch": "ECE",
        "academic_year": "2",
        "minority_eligibility": False,
        "disability_eligibility": False,
        "hosteller_eligibility": True,
        "day_scholar_eligibility": False,
        "required_documents": "Project summary, marksheets, hostel certificate",
        "application_link": "https://example.org/tech-excellence/apply",
        "official_website": "https://example.org/tech-excellence",
        "application_start_date": "2026-07-10",
        "application_end_date": "2026-08-10",
        "status": "published",
        "is_featured": False,
        "trending_score": 72,
        "description": "Focused support for second-year ECE students with strong academic discipline.",
        "benefits": "One-time grant and mentorship access.",
        "selection_process": "Academic screening plus statement-of-purpose review.",
        "is_renewable": False,
        "categories": ["general", "obc", "merit"],
        "states": ["MH", "TN", "GJ"],
    },
    {
        "scholarship_name": "Minority Innovation Scholarship",
        "provider_name": "Innovation and Inclusion Trust",
        "scholarship_type": "private",
        "scholarship_amount": "35000",
        "eligibility_description": "Scholarship for minority B.Tech students building strong technical projects.",
        "minimum_cgpa": "7.2",
        "maximum_family_income": "500000",
        "gender": "all",
        "degree": "B.Tech",
        "branch": "IT",
        "academic_year": "4",
        "minority_eligibility": True,
        "disability_eligibility": False,
        "hosteller_eligibility": False,
        "day_scholar_eligibility": False,
        "required_documents": "Minority certificate, final-year marksheets, project abstract",
        "application_link": "https://example.org/minority-innovation/apply",
        "official_website": "https://example.org/minority-innovation",
        "application_start_date": "2026-07-05",
        "application_end_date": "2026-09-01",
        "status": "published",
        "is_featured": False,
        "trending_score": 68,
        "description": "Helps final-year minority students continue project-focused technical education.",
        "benefits": "Financial aid plus showcase opportunities.",
        "selection_process": "Eligibility review and innovation statement screening.",
        "is_renewable": False,
        "categories": ["minority", "obc"],
        "states": ["UP", "WB", "DL"],
    },
]

DEFAULT_ADMIN_FULL_NAME = "Administrator"
DEFAULT_ADMIN_EMAIL = "admin@scholarai.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123"


def initialize_database():
    """Create all configured database tables and seed first-run data."""
    app = create_app()
    with app.app_context():
        db.create_all()
        _seed_master_data()
        default_admin_created = _ensure_default_admin()
        seeded_scholarships = _seed_sample_scholarships()
        _seed_content_placeholders()
        _print_database_status(seeded_scholarships, default_admin_created)


def _seed_master_data() -> None:
    """Seed categories and states when missing."""
    if Category.query.count() == 0:
        db.session.add_all(
            [
                Category(name=name, slug=slug, description=description)
                for name, slug, description in CATEGORY_SEEDS
            ]
        )

    if State.query.count() == 0:
        db.session.add_all(
            [
                State(name=name, code=code, is_union_territory=is_union_territory)
                for name, code, is_union_territory in STATE_SEEDS
            ]
        )
    db.session.commit()


def _seed_sample_scholarships() -> int:
    """Seed realistic scholarship records on first run only."""
    if Scholarship.query.count() > 0:
        return 0

    created_count = 0
    for payload in SAMPLE_SCHOLARSHIPS:
        ScholarshipService.create_scholarship(payload)
        created_count += 1
    return created_count


def _ensure_default_admin() -> bool:
    """Create the default admin when the admin table is empty."""
    if Admin.query.count() > 0:
        return False

    admin = Admin(
        full_name=DEFAULT_ADMIN_FULL_NAME,
        email=DEFAULT_ADMIN_EMAIL,
        password_hash=generate_password_hash(DEFAULT_ADMIN_PASSWORD),
    )
    db.session.add(admin)
    db.session.commit()
    return True


def _seed_content_placeholders() -> None:
    """Seed lightweight content so public pages are not empty on first run."""
    if News.query.count() == 0:
        ContentService.create_news(
            {
                "title": "ScholarAI Sample Update",
                "summary": "The sample database has been initialized successfully.",
                "content": "This starter news item confirms that the platform content module is working after initialization.",
                "source_url": "https://example.org/scholarai-update",
                "image_url": "",
                "priority": 3,
                "is_published": True,
                "related_scholarship_id": None,
            }
        )

    if FAQ.query.count() == 0:
        ContentService.create_faq(
            {
                "question": "How does ScholarAI calculate eligibility?",
                "answer": "ScholarAI uses backend rules such as income, category, state, degree, branch, year, and CGPA to compute eligibility scores.",
                "display_order": 1,
                "is_published": True,
            }
        )

    if Notification.query.count() == 0:
        ContentService.create_notification(
            {
                "title": "Welcome to ScholarAI",
                "message": "Your sample database is ready. Explore scholarships, deadlines, and recommendations now.",
                "notification_type": "general",
                "audience_type": "all",
                "is_active": True,
                "starts_at": "",
                "ends_at": "",
                "related_scholarship_id": None,
            }
        )


def _print_database_status(seeded_scholarships: int, default_admin_created: bool) -> None:
    """Print a compact database setup summary."""
    inspector = inspect(db.engine)
    tables = sorted(inspector.get_table_names())
    print("ScholarAI database initialized successfully.")
    print(f"Tables created: {', '.join(tables)}")
    print(f"Current admins in database: {Admin.query.count()}")
    if seeded_scholarships:
        print(f"Sample scholarships seeded: {seeded_scholarships}")
    if default_admin_created:
        print("Default admin created:")
        print(f"  Full Name: {DEFAULT_ADMIN_FULL_NAME}")
        print(f"  Email: {DEFAULT_ADMIN_EMAIL}")
        print(f"  Password: {DEFAULT_ADMIN_PASSWORD}")
    elif Admin.query.filter_by(email=DEFAULT_ADMIN_EMAIL).first() is not None:
        print("Default admin credentials:")
        print(f"  Full Name: {DEFAULT_ADMIN_FULL_NAME}")
        print(f"  Email: {DEFAULT_ADMIN_EMAIL}")
        print(f"  Password: {DEFAULT_ADMIN_PASSWORD}")
    print(f"Current scholarships in database: {Scholarship.query.count()}")
    print(f"Current categories in database: {Category.query.count()}")
    print(f"Current states in database: {State.query.count()}")


if __name__ == "__main__":
    initialize_database()
