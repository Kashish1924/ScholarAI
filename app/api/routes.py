from flask import Blueprint, request

from app.services.analytics_service import AnalyticsService
from app.services.content_service import ContentService
from app.services.eligibility_service import EligibilityService
from app.services.scholarship_service import ScholarshipService
from app.utils.api import error_response, success_response
from app.utils.validation import ValidationError


api_bp = Blueprint("api", __name__)


@api_bp.get("/status")
def api_status():
    """Return API availability status."""
    return {
        "status": "success",
        "message": "ScholarAI API is available.",
        "version": "v1",
    }, 200


@api_bp.get("/scholarships")
def list_scholarships():
    """Return scholarships with optional filters and pagination."""
    filters = {
        "keyword": request.args.get("keyword", type=str),
        "scholarship_type": request.args.get("scholarship_type", type=str),
        "state_code": request.args.get("state_code", type=str),
        "category_slug": request.args.get("category_slug", type=str),
        "gender": request.args.get("gender", type=str),
        "degree": request.args.get("degree", type=str),
        "branch": request.args.get("branch", type=str),
        "academic_year": request.args.get("academic_year", type=str),
        "max_income": request.args.get("max_income", type=float),
        "min_cgpa": request.args.get("min_cgpa", type=float),
        "is_featured": request.args.get("is_featured", type=str),
        "deadline_within_days": request.args.get("deadline_within_days", type=int),
        "status": request.args.get("status", default="published", type=str),
    }
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    result = ScholarshipService.list_scholarships(filters=filters, page=page, per_page=per_page)
    return success_response(
        message="Scholarships fetched successfully.",
        data=result,
    )


@api_bp.get("/search")
def search_scholarships():
    """Alias endpoint for search-driven clients."""
    filters = {
        "keyword": request.args.get("q", type=str) or request.args.get("keyword", type=str),
        "scholarship_type": request.args.get("scholarship_type", type=str),
        "state_code": request.args.get("state_code", type=str),
        "category_slug": request.args.get("category_slug", type=str),
        "gender": request.args.get("gender", type=str),
        "degree": request.args.get("degree", type=str),
        "branch": request.args.get("branch", type=str),
        "academic_year": request.args.get("academic_year", type=str),
        "max_income": request.args.get("max_income", type=float),
        "min_cgpa": request.args.get("min_cgpa", type=float),
        "deadline_within_days": request.args.get("deadline_within_days", type=int),
        "status": request.args.get("status", default="published", type=str),
    }
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    result = ScholarshipService.list_scholarships(filters=filters, page=page, per_page=per_page)
    return success_response("Search results fetched successfully.", data=result)


@api_bp.get("/filters")
def get_filter_options():
    """Return reusable filter options for frontend clients."""
    return success_response(
        "Filter options fetched successfully.",
        data=ScholarshipService.get_filter_options(),
    )


@api_bp.get("/scholarships/<int:scholarship_id>")
def get_scholarship(scholarship_id: int):
    """Return a scholarship by id."""
    scholarship = ScholarshipService.get_scholarship_by_id(scholarship_id)
    if scholarship is None:
        return error_response("Scholarship not found.", status_code=404)

    return success_response(
        message="Scholarship fetched successfully.",
        data=ScholarshipService.serialize_scholarship(scholarship),
    )


@api_bp.post("/scholarships")
def create_scholarship():
    """Create a scholarship record from JSON payload."""
    payload = request.get_json(silent=True)
    if payload is None:
        return error_response("Request body must be valid JSON.", status_code=400)

    try:
        scholarship = ScholarshipService.create_scholarship(payload)
    except ValidationError as exc:
        return error_response(
            "Scholarship validation failed.",
            errors=exc.errors,
            status_code=422,
        )

    return success_response(
        message="Scholarship created successfully.",
        data=ScholarshipService.serialize_scholarship(scholarship),
        status_code=201,
    )


@api_bp.put("/scholarships/<int:scholarship_id>")
def update_scholarship(scholarship_id: int):
    """Update a scholarship record from JSON payload."""
    payload = request.get_json(silent=True)
    if payload is None:
        return error_response("Request body must be valid JSON.", status_code=400)

    try:
        scholarship = ScholarshipService.update_scholarship(scholarship_id, payload)
    except ValidationError as exc:
        return error_response(
            "Scholarship validation failed.",
            errors=exc.errors,
            status_code=422,
        )

    if scholarship is None:
        return error_response("Scholarship not found.", status_code=404)

    return success_response(
        message="Scholarship updated successfully.",
        data=ScholarshipService.serialize_scholarship(scholarship),
    )


@api_bp.delete("/scholarships/<int:scholarship_id>")
def delete_scholarship(scholarship_id: int):
    """Delete a scholarship by id."""
    deleted = ScholarshipService.delete_scholarship(scholarship_id)
    if not deleted:
        return error_response("Scholarship not found.", status_code=404)

    return success_response(message="Scholarship deleted successfully.", data=None)


@api_bp.get("/comparison")
def comparison_preview():
    """Return comparison payload for selected scholarship ids."""
    raw_ids = request.args.get("ids", "")
    scholarship_ids = _parse_id_list(raw_ids)
    if not scholarship_ids:
        return error_response(
            "At least one scholarship id is required.",
            errors={"ids": ["Provide comma-separated scholarship ids."]},
            status_code=422,
        )

    items = ScholarshipService.get_comparison_data(scholarship_ids[:3])
    return success_response(
        "Comparison data fetched successfully.",
        data={"items": items, "selected_ids": scholarship_ids[:3]},
    )


@api_bp.post("/comparison")
def comparison_preview_post():
    """Return comparison payload from JSON body."""
    payload = request.get_json(silent=True)
    if payload is None:
        return error_response("Request body must be valid JSON.", status_code=400)

    scholarship_ids = payload.get("scholarship_ids", [])
    if not isinstance(scholarship_ids, list) or not scholarship_ids:
        return error_response(
            "Comparison validation failed.",
            errors={"scholarship_ids": ["Provide a non-empty list of scholarship ids."]},
            status_code=422,
        )

    clean_ids = [int(item) for item in scholarship_ids if str(item).isdigit()][:3]
    if not clean_ids:
        return error_response(
            "Comparison validation failed.",
            errors={"scholarship_ids": ["No valid scholarship ids were provided."]},
            status_code=422,
        )

    items = ScholarshipService.get_comparison_data(clean_ids)
    return success_response(
        "Comparison data fetched successfully.",
        data={"items": items, "selected_ids": clean_ids},
    )


@api_bp.get("/trending")
def trending_scholarships():
    """Return trending scholarships."""
    items = ScholarshipService.get_homepage_sections()["trending"]
    return success_response("Trending scholarships fetched successfully.", data=items)


@api_bp.get("/deadlines")
def deadline_scholarships():
    """Return scholarships closing within a requested number of days."""
    days = request.args.get("within_days", default=7, type=int)
    result = ScholarshipService.list_scholarships(
        filters={"deadline_within_days": max(days, 0), "status": "published"},
        page=1,
        per_page=min(request.args.get("per_page", default=10, type=int), 50),
    )
    return success_response("Deadline scholarships fetched successfully.", data=result)


@api_bp.get("/news")
def list_news():
    """Return published news records."""
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    data = ContentService.list_news(page=page, per_page=per_page, published_only=True)
    return success_response("News fetched successfully.", data=data)


@api_bp.get("/faqs")
def list_faqs():
    """Return published FAQs."""
    data = ContentService.list_faqs(published_only=True)
    return success_response("FAQs fetched successfully.", data=data)


@api_bp.get("/notifications")
def list_notifications():
    """Return active notifications."""
    audience_type = request.args.get("audience_type", default="all", type=str)
    data = ContentService.list_active_notifications(audience_type=audience_type)
    return success_response("Notifications fetched successfully.", data=data)


@api_bp.get("/analytics")
def analytics_summary():
    """Return admin analytics summary payload."""
    return success_response(
        "Analytics fetched successfully.",
        data=AnalyticsService.get_dashboard_analytics(),
    )


@api_bp.post("/eligibility/check")
def eligibility_check():
    """Run deterministic eligibility scoring for a student profile."""
    payload = request.get_json(silent=True)
    if payload is None:
        return error_response("Request body must be valid JSON.", status_code=400)

    try:
        result = EligibilityService.evaluate_student_profile(payload)
    except ValidationError as exc:
        return error_response(
            "Eligibility validation failed.",
            errors=exc.errors,
            status_code=422,
        )

    return success_response("Eligibility evaluated successfully.", data=result)


@api_bp.get("/recommendations")
def recommendations():
    """Return backend-driven scholarship recommendations from query input."""
    payload = {
        "income": request.args.get("income", type=float),
        "cgpa": request.args.get("cgpa", type=float),
        "category_slug": request.args.get("category_slug", type=str),
        "state_code": request.args.get("state_code", type=str),
        "gender": request.args.get("gender", type=str),
        "degree": request.args.get("degree", type=str),
        "branch": request.args.get("branch", type=str),
        "academic_year": request.args.get("academic_year", type=str),
        "minority": request.args.get("minority", default="false", type=str),
        "disability": request.args.get("disability", default="false", type=str),
        "hosteller": request.args.get("hosteller", default="false", type=str),
        "day_scholar": request.args.get("day_scholar", default="false", type=str),
    }
    try:
        result = EligibilityService.evaluate_student_profile(payload)
    except ValidationError as exc:
        return error_response(
            "Recommendation input validation failed.",
            errors=exc.errors,
            status_code=422,
        )
    return success_response("Recommendations fetched successfully.", data=result)


@api_bp.get("/deadline-reminders")
def deadline_reminders():
    """Return deadline reminder buckets."""
    within_days = request.args.get("within_days", default=30, type=int)
    data = EligibilityService.get_deadline_reminders(within_days=within_days)
    return success_response("Deadline reminders fetched successfully.", data=data)


@api_bp.get("/fraud-checks")
def fraud_checks():
    """Return rule-based suspicious scholarship warnings."""
    data = EligibilityService.run_fraud_checks_for_all()
    return success_response("Fraud checks completed successfully.", data=data)


def _parse_id_list(raw_ids: str) -> list[int]:
    """Parse comma-separated ids into integers."""
    parsed = []
    for item in (raw_ids or "").split(","):
        cleaned = item.strip()
        if cleaned.isdigit():
            parsed.append(int(cleaned))
    return parsed
