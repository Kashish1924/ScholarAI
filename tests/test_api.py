import unittest

from app import create_app
from app.extensions import db
from tests.test_data import seed_test_database


class ApiTestCase(unittest.TestCase):
    """Integration tests for the ScholarAI REST API."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            seed_test_database()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_status_endpoint_returns_success(self):
        response = self.client.get("/api/v1/status")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "success")

    def test_filters_endpoint_returns_taxonomy(self):
        response = self.client.get("/api/v1/filters")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("categories", payload["data"])
        self.assertIn("states", payload["data"])

    def test_search_endpoint_returns_matching_scholarship(self):
        response = self.client.get("/api/v1/search?q=Merit")
        self.assertEqual(response.status_code, 200)
        items = response.get_json()["data"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["slug"], "merit-support-scholarship")

    def test_eligibility_endpoint_returns_ranked_results(self):
        payload = {
            "income": 250000,
            "cgpa": 8.2,
            "category_slug": "obc",
            "state_code": "DL",
            "gender": "all",
            "degree": "B.Tech",
            "branch": "CSE",
            "academic_year": "3",
            "minority": False,
            "disability": False,
            "hosteller": False,
            "day_scholar": False,
        }
        response = self.client.post("/api/v1/eligibility/check", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertGreaterEqual(data["counts"]["eligible"], 1)
        self.assertEqual(data["results"][0]["status_label"], "eligible")

    def test_eligibility_endpoint_rejects_unknown_category(self):
        payload = {
            "income": 250000,
            "cgpa": 8.2,
            "category_slug": "unknown",
            "state_code": "DL",
            "gender": "all",
            "degree": "B.Tech",
            "branch": "CSE",
            "academic_year": "3",
            "minority": False,
            "disability": False,
            "hosteller": False,
            "day_scholar": False,
        }
        response = self.client.post("/api/v1/eligibility/check", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertIn("category_slug", response.get_json()["errors"])

    def test_comparison_endpoint_requires_ids(self):
        response = self.client.get("/api/v1/comparison")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["status"], "error")

    def test_fraud_checks_flag_problematic_records(self):
        response = self.client.get("/api/v1/fraud-checks")
        self.assertEqual(response.status_code, 200)
        records = response.get_json()["data"]
        warning_records = [item for item in records if item["status"] == "warning"]
        self.assertTrue(any(item["scholarship_name"] == "Legacy Private Grant" for item in warning_records))

    def test_deadline_reminders_return_bucketed_data(self):
        response = self.client.get("/api/v1/deadline-reminders?within_days=30")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]
        self.assertIn("7", [str(key) for key in payload["scholarships"].keys()])

    def test_taxonomy_create_endpoint_requires_admin_session(self):
        response = self.client.post(
            "/api/v1/taxonomy/categories",
            json={"name": "Test Category", "slug": "test-category"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["status"], "error")


if __name__ == "__main__":
    unittest.main()
