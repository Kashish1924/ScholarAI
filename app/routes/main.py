from flask import Blueprint, render_template


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    """Render the landing page."""
    return render_template("home.html")


@main_bp.get("/health")
def health_check():
    """Return a lightweight health response."""
    return {"status": "success", "message": "ScholarAI is running."}, 200
