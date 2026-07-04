from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.admin.helpers import build_scholarship_payload_from_form, scholarship_to_form_payload
from app.authentication.decorators import admin_login_required
from app.authentication.forms import AdminLoginForm, ScholarshipForm
from app.services.activity_log_service import ActivityLogService
from app.services.admin_service import AdminService
from app.services.scholarship_service import ScholarshipService
from app.utils.validation import ValidationError


admin_bp = Blueprint("admin", __name__, template_folder="../templates")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an admin and start a session."""
    if session.get("admin_id"):
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = AdminService.authenticate_admin(form.email.data, form.password.data)
        if admin is None:
            flash("Invalid email or password.", "danger")
            return render_template("admin/login.html", form=form)

        session["admin_id"] = admin.admin_id
        session["admin_name"] = admin.full_name
        session.permanent = bool(form.remember_me.data)
        admin.last_login_at = datetime.now(timezone.utc)
        from app.extensions import db

        db.session.commit()
        ActivityLogService.log_admin_activity(
            admin_id=admin.admin_id,
            action_type="login",
            entity_type="admin",
            entity_id=admin.admin_id,
            description="Admin logged into the dashboard.",
        )
        flash("Welcome back to ScholarAI admin.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.html", form=form)


@admin_bp.get("/dashboard")
@admin_login_required
def dashboard():
    """Render the admin dashboard."""
    summary = AdminService.get_dashboard_summary()
    scholarships = ScholarshipService.list_for_admin(limit=10)
    return render_template(
        "admin/dashboard.html",
        summary=summary,
        scholarships=scholarships,
    )


@admin_bp.post("/logout")
@admin_login_required
def logout():
    """Terminate the active admin session."""
    admin_id = session.get("admin_id")
    ActivityLogService.log_admin_activity(
        admin_id=admin_id,
        action_type="logout",
        entity_type="admin",
        entity_id=admin_id,
        description="Admin logged out of the dashboard.",
    )
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin.login"))


@admin_bp.get("/scholarships")
@admin_login_required
def scholarship_list():
    """Render the scholarship management table."""
    scholarships = ScholarshipService.list_for_admin(limit=100)
    return render_template("admin/manage_scholarships.html", scholarships=scholarships)


@admin_bp.route("/scholarships/add", methods=["GET", "POST"])
@admin_login_required
def add_scholarship():
    """Render and process scholarship creation."""
    form = ScholarshipForm()
    if form.validate_on_submit():
        payload = build_scholarship_payload_from_form(form)
        try:
            scholarship = ScholarshipService.create_scholarship(payload)
        except ValidationError as exc:
            for field_name, field_errors in exc.errors.items():
                target = getattr(form, field_name, None)
                if target is not None:
                    target.errors.extend(field_errors)
                else:
                    for error in field_errors:
                        flash(error, "danger")
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="create",
                entity_type="scholarship",
                entity_id=scholarship.scholarship_id,
                description=f"Created scholarship {scholarship.scholarship_name}.",
            )
            flash("Scholarship created successfully.", "success")
            return redirect(url_for("admin.scholarship_list"))

    return render_template(
        "admin/scholarship_form.html",
        form=form,
        page_title="Add Scholarship",
        submit_label="Create Scholarship",
    )


@admin_bp.route("/scholarships/<int:scholarship_id>/edit", methods=["GET", "POST"])
@admin_login_required
def edit_scholarship(scholarship_id: int):
    """Render and process scholarship updates."""
    scholarship = ScholarshipService.get_scholarship_by_id(scholarship_id)
    if scholarship is None:
        flash("Scholarship not found.", "danger")
        return redirect(url_for("admin.scholarship_list"))

    form = ScholarshipForm(data=scholarship_to_form_payload(scholarship))
    if form.validate_on_submit():
        payload = build_scholarship_payload_from_form(form)
        try:
            updated = ScholarshipService.update_scholarship(scholarship_id, payload)
        except ValidationError as exc:
            for field_name, field_errors in exc.errors.items():
                target = getattr(form, field_name, None)
                if target is not None:
                    target.errors.extend(field_errors)
                else:
                    for error in field_errors:
                        flash(error, "danger")
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="update",
                entity_type="scholarship",
                entity_id=scholarship_id,
                description=f"Updated scholarship {updated.scholarship_name}.",
            )
            flash("Scholarship updated successfully.", "success")
            return redirect(url_for("admin.scholarship_list"))

    return render_template(
        "admin/scholarship_form.html",
        form=form,
        page_title="Edit Scholarship",
        submit_label="Update Scholarship",
    )


@admin_bp.post("/scholarships/<int:scholarship_id>/delete")
@admin_login_required
def delete_scholarship(scholarship_id: int):
    """Delete a scholarship from the admin interface."""
    scholarship = ScholarshipService.get_scholarship_by_id(scholarship_id)
    if scholarship is None:
        flash("Scholarship not found.", "danger")
        return redirect(url_for("admin.scholarship_list"))

    scholarship_name = scholarship.scholarship_name
    deleted = ScholarshipService.delete_scholarship(scholarship_id)
    if deleted:
        ActivityLogService.log_admin_activity(
            admin_id=session.get("admin_id"),
            action_type="delete",
            entity_type="scholarship",
            entity_id=scholarship_id,
            description=f"Deleted scholarship {scholarship_name}.",
        )
        flash("Scholarship deleted successfully.", "success")
    else:
        flash("Scholarship could not be deleted.", "danger")
    return redirect(url_for("admin.scholarship_list"))
