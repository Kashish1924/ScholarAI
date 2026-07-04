from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.admin.content_helpers import (
    build_faq_payload_from_form,
    build_news_payload_from_form,
    build_notification_payload_from_form,
    faq_to_form_payload,
    news_to_form_payload,
    notification_to_form_payload,
)
from app.admin.helpers import build_scholarship_payload_from_form, scholarship_to_form_payload
from app.authentication.decorators import admin_login_required
from app.authentication.forms import AdminLoginForm, FAQForm, NewsForm, NotificationForm, ScholarshipForm
from app.services.activity_log_service import ActivityLogService
from app.services.admin_service import AdminService
from app.services.content_service import ContentService
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


@admin_bp.get("/news")
@admin_login_required
def news_list():
    """Render news management table."""
    news_items = ContentService.list_news_records(limit=100)
    return render_template("admin/manage_news.html", news_items=news_items)


@admin_bp.route("/news/add", methods=["GET", "POST"])
@admin_login_required
def add_news():
    """Render and process news creation."""
    form = NewsForm()
    if form.validate_on_submit():
        payload = build_news_payload_from_form(form)
        try:
            news = ContentService.create_news(payload, admin_id=session.get("admin_id"))
        except ValidationError as exc:
            _attach_form_errors(form, exc.errors)
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="create",
                entity_type="news",
                entity_id=news.news_id,
                description=f"Created news item {news.title}.",
            )
            flash("News item created successfully.", "success")
            return redirect(url_for("admin.news_list"))
    return render_template("admin/news_form.html", form=form, page_title="Add News", submit_label="Create News")


@admin_bp.route("/news/<int:news_id>/edit", methods=["GET", "POST"])
@admin_login_required
def edit_news(news_id: int):
    """Render and process news updates."""
    news = ContentService.get_news_by_id(news_id)
    if news is None:
        flash("News item not found.", "danger")
        return redirect(url_for("admin.news_list"))
    form = NewsForm(data=news_to_form_payload(news))
    if form.validate_on_submit():
        payload = build_news_payload_from_form(form)
        try:
            updated = ContentService.update_news(news_id, payload)
        except ValidationError as exc:
            _attach_form_errors(form, exc.errors)
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="update",
                entity_type="news",
                entity_id=news_id,
                description=f"Updated news item {updated.title}.",
            )
            flash("News item updated successfully.", "success")
            return redirect(url_for("admin.news_list"))
    return render_template("admin/news_form.html", form=form, page_title="Edit News", submit_label="Update News")


@admin_bp.post("/news/<int:news_id>/delete")
@admin_login_required
def delete_news(news_id: int):
    """Delete a news item."""
    news = ContentService.get_news_by_id(news_id)
    if news is None:
        flash("News item not found.", "danger")
        return redirect(url_for("admin.news_list"))
    title = news.title
    ContentService.delete_news(news_id)
    ActivityLogService.log_admin_activity(
        admin_id=session.get("admin_id"),
        action_type="delete",
        entity_type="news",
        entity_id=news_id,
        description=f"Deleted news item {title}.",
    )
    flash("News item deleted successfully.", "success")
    return redirect(url_for("admin.news_list"))


@admin_bp.get("/faqs")
@admin_login_required
def faq_list():
    """Render FAQ management table."""
    faqs = ContentService.list_faq_records()
    return render_template("admin/manage_faqs.html", faqs=faqs)


@admin_bp.route("/faqs/add", methods=["GET", "POST"])
@admin_login_required
def add_faq():
    """Render and process FAQ creation."""
    form = FAQForm()
    if form.validate_on_submit():
        try:
            faq = ContentService.create_faq(
                build_faq_payload_from_form(form),
                admin_id=session.get("admin_id"),
            )
        except ValidationError as exc:
            _attach_form_errors(form, exc.errors)
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="create",
                entity_type="faq",
                entity_id=faq.faq_id,
                description=f"Created FAQ {faq.question}.",
            )
            flash("FAQ created successfully.", "success")
            return redirect(url_for("admin.faq_list"))
    return render_template("admin/faq_form.html", form=form, page_title="Add FAQ", submit_label="Create FAQ")


@admin_bp.route("/faqs/<int:faq_id>/edit", methods=["GET", "POST"])
@admin_login_required
def edit_faq(faq_id: int):
    """Render and process FAQ updates."""
    faq = ContentService.get_faq_by_id(faq_id)
    if faq is None:
        flash("FAQ not found.", "danger")
        return redirect(url_for("admin.faq_list"))
    form = FAQForm(data=faq_to_form_payload(faq))
    if form.validate_on_submit():
        try:
            updated = ContentService.update_faq(faq_id, build_faq_payload_from_form(form))
        except ValidationError as exc:
            _attach_form_errors(form, exc.errors)
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="update",
                entity_type="faq",
                entity_id=faq_id,
                description=f"Updated FAQ {updated.question}.",
            )
            flash("FAQ updated successfully.", "success")
            return redirect(url_for("admin.faq_list"))
    return render_template("admin/faq_form.html", form=form, page_title="Edit FAQ", submit_label="Update FAQ")


@admin_bp.post("/faqs/<int:faq_id>/delete")
@admin_login_required
def delete_faq(faq_id: int):
    """Delete an FAQ."""
    faq = ContentService.get_faq_by_id(faq_id)
    if faq is None:
        flash("FAQ not found.", "danger")
        return redirect(url_for("admin.faq_list"))
    question = faq.question
    ContentService.delete_faq(faq_id)
    ActivityLogService.log_admin_activity(
        admin_id=session.get("admin_id"),
        action_type="delete",
        entity_type="faq",
        entity_id=faq_id,
        description=f"Deleted FAQ {question}.",
    )
    flash("FAQ deleted successfully.", "success")
    return redirect(url_for("admin.faq_list"))


@admin_bp.get("/notifications")
@admin_login_required
def notification_list():
    """Render notification management table."""
    notifications = ContentService.list_notification_records()
    return render_template("admin/manage_notifications.html", notifications=notifications)


@admin_bp.route("/notifications/add", methods=["GET", "POST"])
@admin_login_required
def add_notification():
    """Render and process notification creation."""
    form = NotificationForm()
    if form.validate_on_submit():
        try:
            notification = ContentService.create_notification(
                build_notification_payload_from_form(form),
                admin_id=session.get("admin_id"),
            )
        except ValidationError as exc:
            _attach_form_errors(form, exc.errors)
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="create",
                entity_type="notification",
                entity_id=notification.notification_id,
                description=f"Created notification {notification.title}.",
            )
            flash("Notification created successfully.", "success")
            return redirect(url_for("admin.notification_list"))
    return render_template(
        "admin/notification_form.html",
        form=form,
        page_title="Add Notification",
        submit_label="Create Notification",
    )


@admin_bp.route("/notifications/<int:notification_id>/edit", methods=["GET", "POST"])
@admin_login_required
def edit_notification(notification_id: int):
    """Render and process notification updates."""
    notification = ContentService.get_notification_by_id(notification_id)
    if notification is None:
        flash("Notification not found.", "danger")
        return redirect(url_for("admin.notification_list"))
    form = NotificationForm(data=notification_to_form_payload(notification))
    if form.validate_on_submit():
        try:
            updated = ContentService.update_notification(
                notification_id,
                build_notification_payload_from_form(form),
            )
        except ValidationError as exc:
            _attach_form_errors(form, exc.errors)
        else:
            ActivityLogService.log_admin_activity(
                admin_id=session.get("admin_id"),
                action_type="update",
                entity_type="notification",
                entity_id=notification_id,
                description=f"Updated notification {updated.title}.",
            )
            flash("Notification updated successfully.", "success")
            return redirect(url_for("admin.notification_list"))
    return render_template(
        "admin/notification_form.html",
        form=form,
        page_title="Edit Notification",
        submit_label="Update Notification",
    )


@admin_bp.post("/notifications/<int:notification_id>/delete")
@admin_login_required
def delete_notification(notification_id: int):
    """Delete a notification."""
    notification = ContentService.get_notification_by_id(notification_id)
    if notification is None:
        flash("Notification not found.", "danger")
        return redirect(url_for("admin.notification_list"))
    title = notification.title
    ContentService.delete_notification(notification_id)
    ActivityLogService.log_admin_activity(
        admin_id=session.get("admin_id"),
        action_type="delete",
        entity_type="notification",
        entity_id=notification_id,
        description=f"Deleted notification {title}.",
    )
    flash("Notification deleted successfully.", "success")
    return redirect(url_for("admin.notification_list"))


def _attach_form_errors(form, errors: dict) -> None:
    """Attach service-layer validation errors to form fields."""
    for field_name, field_errors in errors.items():
        target = getattr(form, field_name, None)
        if target is not None:
            target.errors.extend(field_errors)
        else:
            for error in field_errors:
                flash(error, "danger")
