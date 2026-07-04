import unittest

from app import create_app
from app.extensions import db
from app.models import Scholarship
from app.services.eligibility_service import EligibilityService
from app.services.scholarship_service import ScholarshipService
from tests.test_data import seed_test_database


class ServiceLayerTestCase(unittest.TestCase):
    """Focused tests for backend service logic."""

    def setUp(self):
        self.app = create_app("testing")
        with self.app.app_context():
            db.create_all()
            seed_test_database()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage_sections_include_featured_items(self):
        with self.app.app_context():
            sections = ScholarshipService.get_homepage_sections()
            self.assertGreaterEqual(len(sections["featured"]), 1)
            self.assertEqual(sections["featured"][0]["slug"], "merit-support-scholarship")

    def test_eligibility_service_marks_hard_gate_failure(self):
        with self.app.app_context():
            payload = {
                "income": 250000,
                "cgpa": 8.0,
                "category_slug": "general",
                "state_code": "MH",
                "gender": "female",
                "degree": "B.Tech",
                "branch": "ECE",
                "academic_year": "2",
                "minority": False,
                "disability": False,
                "hosteller": False,
                "day_scholar": False,
            }
            result = EligibilityService.evaluate_student_profile(payload)
            flagged = next(
                item
                for item in result["results"]
                if item["scholarship"]["slug"] == "legacy-private-grant"
            )
            self.assertEqual(flagged["status_label"], "not_eligible")

    def test_fraud_check_detects_missing_official_website(self):
        with self.app.app_context():
            scholarship = Scholarship.query.filter_by(slug="legacy-private-grant").first()
            result = EligibilityService.run_fraud_checks(scholarship)
            self.assertEqual(result["status"], "warning")
            self.assertTrue(any("Official website is missing." == item for item in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
