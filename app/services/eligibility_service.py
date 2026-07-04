from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from app.ai.ai_service import eligibility_explanation
from app.models import Scholarship
from app.services.scholarship_service import ScholarshipService
from app.utils.validation import EligibilityInputValidator, ValidationError


@dataclass(frozen=True)
class EligibilityWeights:
    income_match: int = 25
    category_match: int = 20
    state_match: int = 15
    degree_match: int = 10
    branch_match: int = 10
    cgpa_match: int = 10
    gender_match: int = 5
    minority_match: int = 3
    disability_match: int = 2


class EligibilityService:
    """Deterministic scholarship eligibility and recommendation engine."""

    WEIGHTS = EligibilityWeights()

    @staticmethod
    def evaluate_student_profile(payload: dict) -> dict:
        """Return ranked scholarship eligibility results for a student profile."""
        clean_payload = EligibilityInputValidator.validate_payload(payload)
        scholarships = Scholarship.query.filter_by(status="published").all()

        results = []
        for scholarship in scholarships:
            evaluation = EligibilityService._evaluate_single_scholarship(
                scholarship=scholarship,
                student=clean_payload,
            )
            results.append(evaluation)

        results.sort(
            key=lambda item: (
                EligibilityService._status_rank(item["status_label"]),
                item["eligibility_score"],
                item["match_breakdown"]["deadline_priority"],
                item["scholarship"]["trending_score"],
            ),
            reverse=True,
        )

        recommended_results = [
            item for item in results if item["status_label"] != "not_eligible"
        ]

        summary = {
            "student_profile": clean_payload,
            "counts": {
                "not_eligible": sum(
                    1 for item in results if item["status_label"] == "not_eligible"
                ),
                "eligible": sum(1 for item in results if item["status_label"] == "eligible"),
                "partially_eligible": sum(
                    1 for item in results if item["status_label"] == "partially_eligible"
                ),
                "total_evaluated": len(results),
                "recommended_matches": len(recommended_results),
            },
            "results": results,
            "recommended_results": recommended_results,
            "ai_explanation": eligibility_explanation(
                student_profile=clean_payload,
                results=recommended_results,
            ),
        }
        return summary

    @staticmethod
    def get_deadline_reminders(within_days: int = 7) -> dict:
        """Return scholarships closing within the requested number of days."""
        within_days = max(within_days, 0)
        today = date.today()
        cutoff = today + timedelta(days=within_days)
        scholarships = Scholarship.query.filter(
            Scholarship.status == "published",
            Scholarship.application_end_date >= today,
            Scholarship.application_end_date <= cutoff,
        ).order_by(Scholarship.application_end_date.asc()).all()

        buckets = {1: [], 3: [], 7: [], 30: []}
        for scholarship in scholarships:
            days_left = (scholarship.application_end_date - today).days
            for bucket in buckets:
                if days_left <= bucket:
                    buckets[bucket].append(
                        {
                            "scholarship_id": scholarship.scholarship_id,
                            "scholarship_name": scholarship.scholarship_name,
                            "deadline": scholarship.application_end_date.isoformat(),
                            "days_left": days_left,
                            "application_link": scholarship.application_link,
                        }
                    )

        return {
            "within_days": within_days,
            "scholarships": buckets,
        }

    @staticmethod
    def run_fraud_checks(scholarship: Scholarship) -> dict:
        """Run simple rule-based suspicious data checks."""
        warnings = []
        today = date.today()

        if not scholarship.provider_name or not scholarship.provider_name.strip():
            warnings.append("Provider name is missing.")

        if not scholarship.official_website or not scholarship.official_website.strip():
            warnings.append("Official website is missing.")

        if scholarship.application_end_date < today:
            warnings.append("Application end date is already expired.")

        if not scholarship.application_link.startswith(("http://", "https://")):
            warnings.append("Application link is invalid.")

        status = "clean" if not warnings else "warning"
        return {
            "scholarship_id": scholarship.scholarship_id,
            "scholarship_name": scholarship.scholarship_name,
            "status": status,
            "warnings": warnings,
        }

    @staticmethod
    def run_fraud_checks_for_all() -> list[dict]:
        """Run rule-based checks across all scholarships."""
        scholarships = Scholarship.query.order_by(Scholarship.created_at.desc()).all()
        return [EligibilityService.run_fraud_checks(item) for item in scholarships]

    @staticmethod
    def _evaluate_single_scholarship(scholarship: Scholarship, student: dict) -> dict:
        """Calculate scholarship eligibility score and breakdown."""
        weights = EligibilityService.WEIGHTS
        score = 0
        breakdown = {}

        income_match = scholarship.maximum_family_income is None or (
            Decimal(str(student["income"])) <= scholarship.maximum_family_income
        )
        breakdown["income_match"] = weights.income_match if income_match else 0
        score += breakdown["income_match"]

        scholarship_categories = {link.category.slug for link in scholarship.categories}
        category_match = not scholarship_categories or student["category_slug"] in scholarship_categories
        breakdown["category_match"] = weights.category_match if category_match else 0
        score += breakdown["category_match"]

        scholarship_states = {link.state.code for link in scholarship.states}
        state_match = not scholarship_states or student["state_code"] in scholarship_states
        breakdown["state_match"] = weights.state_match if state_match else 0
        score += breakdown["state_match"]

        degree_match = scholarship.degree.lower() == student["degree"].lower()
        breakdown["degree_match"] = weights.degree_match if degree_match else 0
        score += breakdown["degree_match"]

        branch_match = scholarship.branch.lower() in {"all", student["branch"].lower()}
        breakdown["branch_match"] = weights.branch_match if branch_match else 0
        score += breakdown["branch_match"]

        cgpa_match = scholarship.minimum_cgpa is None or (
            Decimal(str(student["cgpa"])) >= scholarship.minimum_cgpa
        )
        breakdown["cgpa_match"] = weights.cgpa_match if cgpa_match else 0
        score += breakdown["cgpa_match"]

        gender_match = scholarship.gender in {"all", student["gender"]}
        breakdown["gender_match"] = weights.gender_match if gender_match else 0
        score += breakdown["gender_match"]

        minority_match = (not scholarship.minority_eligibility) or student["minority"]
        breakdown["minority_match"] = weights.minority_match if minority_match else 0
        score += breakdown["minority_match"]

        disability_match = (not scholarship.disability_eligibility) or student["disability"]
        breakdown["disability_match"] = weights.disability_match if disability_match else 0
        score += breakdown["disability_match"]

        hosteller_gate = (not scholarship.hosteller_eligibility) or student["hosteller"]
        day_scholar_gate = (not scholarship.day_scholar_eligibility) or student["day_scholar"]
        year_match = scholarship.academic_year in {"all", student["academic_year"]}

        hard_failures = []
        if not hosteller_gate:
            hard_failures.append("Hosteller eligibility requirement not met.")
        if not day_scholar_gate:
            hard_failures.append("Day scholar eligibility requirement not met.")
        if not year_match:
            hard_failures.append("Academic year requirement not met.")

        status_label = EligibilityService._determine_status(score=score, hard_failures=hard_failures)
        deadline_priority = EligibilityService._deadline_priority(scholarship.application_end_date)

        explanation_points = []
        if income_match:
            explanation_points.append("Family income fits the scholarship limit.")
        if category_match:
            explanation_points.append("Category requirement is satisfied.")
        if state_match:
            explanation_points.append("State eligibility is satisfied.")
        if degree_match and branch_match:
            explanation_points.append("Degree and branch match the scholarship criteria.")
        if cgpa_match:
            explanation_points.append("CGPA meets the minimum threshold.")
        if gender_match:
            explanation_points.append("Gender eligibility is satisfied.")
        explanation_points.extend(hard_failures)

        return {
            "scholarship": ScholarshipService.serialize_scholarship(scholarship),
            "eligibility_score": score,
            "status_label": status_label,
            "eligible": status_label == "eligible",
            "match_breakdown": {
                **breakdown,
                "hosteller_gate": hosteller_gate,
                "day_scholar_gate": day_scholar_gate,
                "year_match": year_match,
                "deadline_priority": deadline_priority,
            },
            "explanation_points": explanation_points,
        }

    @staticmethod
    def _determine_status(score: int, hard_failures: list[str]) -> str:
        """Convert score and hard failures into a human-readable eligibility status."""
        if hard_failures:
            return "not_eligible"
        if score >= 75:
            return "eligible"
        if score >= 45:
            return "partially_eligible"
        return "not_eligible"

    @staticmethod
    def _deadline_priority(deadline: date) -> int:
        """Return urgency weighting based on deadline proximity."""
        days_left = (deadline - date.today()).days
        if days_left <= 3:
            return 30
        if days_left <= 7:
            return 20
        if days_left <= 30:
            return 10
        return 0

    @staticmethod
    def _status_rank(status_label: str) -> int:
        """Rank eligibility statuses for sorting."""
        ranks = {
            "eligible": 3,
            "partially_eligible": 2,
            "not_eligible": 1,
        }
        return ranks.get(status_label, 0)
