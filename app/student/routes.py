from flask import Blueprint, abort, render_template, request

from app.services.scholarship_service import ScholarshipService


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
    page = request.args.get("page", default=1, type=int)
    result = ScholarshipService.list_scholarships(filters=filters, page=page, per_page=9)
    return render_template(
        "student/scholarships.html",
        result=result,
        filters=filters,
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
    return render_template(
        "student/scholarship_detail.html",
        scholarship=ScholarshipService.serialize_scholarship(scholarship),
        related_items=related_items,
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
    )


@student_bp.get("/eligibility-checker")
def eligibility_checker():
    """Render the eligibility checker scaffold page."""
    return render_template("student/eligibility_checker.html")
