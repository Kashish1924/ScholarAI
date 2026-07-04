from flask import Blueprint, render_template

from app.services.scholarship_service import ScholarshipService


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    """Render the landing page."""
    sections = ScholarshipService.get_homepage_sections()
    return render_template("home.html", sections=sections)


@main_bp.get("/health")
def health_check():
    """Return a lightweight health response."""
    return {"status": "success", "message": "ScholarAI is running."}, 200
