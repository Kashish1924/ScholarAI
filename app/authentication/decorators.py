from functools import wraps

from flask import flash, redirect, session, url_for
from app.services.admin_service import AdminService


def admin_login_required(view_func):
    """Protect admin views behind an authenticated admin session."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        admin_id = session.get("admin_id")
        if not admin_id:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("admin.login"))
        admin = AdminService.get_admin_by_id(admin_id)
        if admin is None:
            session.clear()
            flash("Your admin session is no longer valid. Please log in again.", "warning")
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)

    return wrapped_view
