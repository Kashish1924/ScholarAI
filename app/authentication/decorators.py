from functools import wraps

from flask import flash, redirect, session, url_for


def admin_login_required(view_func):
    """Protect admin views behind an authenticated admin session."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)

    return wrapped_view
