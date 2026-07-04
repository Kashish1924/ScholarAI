from flask import Blueprint, render_template


student_bp = Blueprint("student", __name__, template_folder="../templates")


@student_bp.get("/scholarships")
def scholarships():
    """Render the student scholarship listing page."""
    return render_template("student/scholarships.html")
