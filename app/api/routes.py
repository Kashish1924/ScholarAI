from flask import Blueprint, request

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
