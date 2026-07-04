from flask import Blueprint, render_template


admin_bp = Blueprint("admin", __name__, template_folder="../templates")


@admin_bp.get("/login")
def login():
    """Render the admin login page."""
    return render_template("admin/login.html")


@admin_bp.get("/dashboard")
def dashboard():
    """Render the admin dashboard."""
    return render_template("admin/dashboard.html")
