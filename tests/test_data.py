from datetime import date, datetime, timedelta, timezone

from app.extensions import db
from app.models import Category, FAQ, News, Notification, Scholarship, ScholarshipCategory, ScholarshipState, State
from app.services.admin_service import AdminService


def seed_test_database():
    """Populate a compact but realistic dataset for automated tests."""
    general = Category(name="General", slug="general", description="General category")
    obc = Category(name="OBC", slug="obc", description="Other Backward Class")
    delhi = State(name="Delhi", code="DL")
    maharashtra = State(name="Maharashtra", code="MH")

    db.session.add_all([general, obc, delhi, maharashtra])
    db.session.flush()

    active_scholarship = Scholarship(
        scholarship_name="Merit Support Scholarship",
        slug="merit-support-scholarship",
        provider_name="National Education Board",
        scholarship_type="government",
        scholarship_amount=50000,
        eligibility_description="For academically strong engineering students.",
        minimum_cgpa=7.5,
        maximum_family_income=300000,
        gender="all",
        degree="B.Tech",
        branch="CSE",
        academic_year="3",
        minority_eligibility=False,
        disability_eligibility=False,
        hosteller_eligibility=False,
        day_scholar_eligibility=False,
        required_documents="Aadhaar, Income Certificate, Marksheet",
        application_link="https://example.org/apply",
        official_website="https://example.org",
        application_start_date=date.today() - timedelta(days=10),
        application_end_date=date.today() + timedelta(days=5),
        status="published",
        is_featured=True,
        trending_score=88,
        description="Support for meritorious students pursuing technology degrees.",
        benefits="Tuition support and stipend.",
        selection_process="Merit-based shortlisting.",
        is_renewable=True,
        view_count=240,
    )

    flagged_scholarship = Scholarship(
        scholarship_name="Legacy Private Grant",
        slug="legacy-private-grant",
        provider_name="Legacy Foundation",
        scholarship_type="private",
        scholarship_amount=25000,
        eligibility_description="Private grant for engineering students.",
        minimum_cgpa=6.0,
        maximum_family_income=600000,
        gender="female",
        degree="B.Tech",
        branch="ECE",
        academic_year="2",
        minority_eligibility=True,
        disability_eligibility=False,
        hosteller_eligibility=True,
        day_scholar_eligibility=False,
        required_documents="Identity proof",
        application_link="invalid-link",
        official_website="",
        application_start_date=date.today() - timedelta(days=90),
        application_end_date=date.today() - timedelta(days=1),
        status="published",
        is_featured=False,
        trending_score=30,
        description="Legacy scholarship kept for fraud-check testing.",
        benefits="One-time cash benefit.",
        selection_process="Document review.",
        is_renewable=False,
        view_count=25,
    )

    db.session.add_all([active_scholarship, flagged_scholarship])
    db.session.flush()

    db.session.add_all(
        [
            ScholarshipCategory(scholarship=active_scholarship, category=obc),
            ScholarshipState(scholarship=active_scholarship, state=delhi),
            ScholarshipCategory(scholarship=flagged_scholarship, category=general),
            ScholarshipState(scholarship=flagged_scholarship, state=maharashtra),
        ]
    )

    news = News(
        title="Scholarship Window Extended",
        slug="scholarship-window-extended",
        summary="Deadline has been extended.",
        content="The ministry has extended the deadline by one week.",
        source_url="https://example.org/news",
        priority=5,
        is_published=True,
        published_at=datetime.now(timezone.utc),
        related_scholarship=active_scholarship,
    )
    faq = FAQ(
        question="How is eligibility calculated?",
        answer="ScholarAI uses backend scoring rules.",
        display_order=1,
        is_published=True,
    )
    notification = Notification(
        title="Complete your shortlist",
        message="Compare scholarships before the closing date.",
        notification_type="reminder",
        audience_type="all",
        is_active=True,
        starts_at=datetime.now(timezone.utc) - timedelta(days=1),
        ends_at=datetime.now(timezone.utc) + timedelta(days=7),
        related_scholarship=active_scholarship,
    )

    db.session.add_all([news, faq, notification])
    AdminService.create_admin(
        full_name="Test Admin",
        email="admin@test.com",
        password="StrongPass123",
    )
    db.session.commit()
