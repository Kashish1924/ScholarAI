from flask import Blueprint, abort, render_template, request

from app.ai.ai_service import (
    chat_assistant,
    compare_scholarships as ai_compare_scholarships,
    generate_email,
    summarize_scholarship,
)
from app.services.content_service import ContentService
from app.services.eligibility_service import EligibilityService
from app.services.scholarship_service import ScholarshipService
from app.utils.validation import ValidationError


student_bp = Blueprint("student", __name__, template_folder="../templates")


@student_bp.get("/scholarships")
def scholarships():
    """Render the student scholarship listing page."""
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
        "deadline_within_days": request.args.get("deadline_within_days", type=int),
        "status": "published",
    }
    search_helper = None
    if filters["keyword"]:
        search_helper = ScholarshipService.interpret_natural_language_query(filters["keyword"])

    effective_filters = dict(filters)
    if search_helper:
        for field_name, field_value in search_helper["filters"].items():
            if not effective_filters.get(field_name):
                effective_filters[field_name] = field_value
    page = request.args.get("page", default=1, type=int)
    result = ScholarshipService.list_scholarships(filters=effective_filters, page=page, per_page=9)
    return render_template(
        "student/scholarships.html",
        result=result,
        filters=effective_filters,
        raw_filters=filters,
        search_helper=search_helper,
    )


@student_bp.get("/scholarships/<slug>")
def scholarship_detail(slug: str):
    """Render the scholarship detail page."""
    scholarship = ScholarshipService.get_scholarship_by_slug(slug)
    if scholarship is None or scholarship.status != "published":
        abort(404)

    related_result = ScholarshipService.list_scholarships(
        filters={
            "branch": scholarship.branch,
            "degree": scholarship.degree,
            "status": "published",
        },
        page=1,
        per_page=3,
    )
    related_items = [
        item for item in related_result["items"] if item["slug"] != scholarship.slug
    ][:3]
    serialized_scholarship = ScholarshipService.serialize_scholarship(scholarship)
    return render_template(
        "student/scholarship_detail.html",
        scholarship=serialized_scholarship,
        related_items=related_items,
        ai_summary=summarize_scholarship(serialized_scholarship),
        email_draft=generate_email(serialized_scholarship),
    )


@student_bp.get("/bookmarks")
def bookmarks():
    """Render the local bookmark page."""
    return render_template("student/bookmarks.html")


@student_bp.get("/compare")
def compare():
    """Render scholarship comparison for selected ids."""
    raw_ids = request.args.get("ids", "")
    scholarship_ids = []
    for item in raw_ids.split(","):
        cleaned = item.strip()
        if cleaned.isdigit():
            scholarship_ids.append(int(cleaned))
    comparison_items = ScholarshipService.get_comparison_data(scholarship_ids[:3])
    return render_template(
        "student/compare.html",
        comparison_items=comparison_items,
        selected_ids=scholarship_ids[:3],
        ai_comparison=ai_compare_scholarships(comparison_items),
    )


@student_bp.get("/news")
def news():
    """Render the scholarship news page."""
    page = request.args.get("page", default=1, type=int)
    news_result = ContentService.list_news(page=page, per_page=9, published_only=True)
    return render_template("student/news.html", news_result=news_result)


@student_bp.get("/faq")
def faq():
    """Render the FAQ page."""
    faqs = ContentService.list_faqs(published_only=True)
    return render_template("student/faq.html", faqs=faqs)


@student_bp.get("/notifications")
def notifications():
    """Render active student notifications."""
    items = ContentService.list_active_notifications(audience_type="student")
    return render_template("student/notifications.html", notifications=items)


@student_bp.get("/trending")
def trending():
    """Render the dedicated trending scholarships page."""
    sections = ScholarshipService.get_homepage_sections()
    return render_template("student/trending.html", items=sections["trending"])


@student_bp.get("/deadlines")
def deadlines():
    """Render scholarships closing soon grouped by urgency."""
    reminders = EligibilityService.get_deadline_reminders(within_days=30)
    return render_template("student/deadlines.html", reminders=reminders)


@student_bp.get("/eligibility-checker")
def eligibility_checker():
    """Render the eligibility checker scaffold page."""
    result = None
    errors = {}
    submitted = False

    if request.args:
        submitted = True
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
            errors = exc.errors

    return render_template(
        "student/eligibility_checker.html",
        result=result,
        errors=errors,
        submitted=submitted,
        filters=ScholarshipService.get_filter_options(),
    )


@student_bp.get("/ai-recommendations")
def ai_recommendations():
    """Render AI-ready recommendations backed by deterministic matching."""
    result = None
    errors = {}
    submitted = False

    if request.args:
        submitted = True
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
            errors = exc.errors

    return render_template(
        "student/ai_recommendations.html",
        result=result,
        errors=errors,
        submitted=submitted,
        filters=ScholarshipService.get_filter_options(),
    )


@student_bp.get("/ai-chat")
def ai_chat():
    """Render the AI-ready chat placeholder page."""
    sections = ScholarshipService.get_homepage_sections()
    starter_context = chat_assistant(
        "How can ScholarAI help me?",
        context={"scholarships": sections["featured"][:2]},
    )
    return render_template(
        "student/ai_chat.html",
        starter_context=starter_context,
    )
