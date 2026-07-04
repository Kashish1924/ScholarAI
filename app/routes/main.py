from flask import Blueprint, flash, redirect, render_template, url_for

from app.authentication.forms import ContactForm
from app.services.content_service import ContentService
from app.services.scholarship_service import ScholarshipService
from app.utils.validation import ValidationError


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


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """Render and process the public contact form."""
    form = ContactForm()
    if form.validate_on_submit():
        try:
            ContentService.create_contact_message(
                {
                    "full_name": form.full_name.data,
                    "email": form.email.data,
                    "subject": form.subject.data,
                    "message": form.message.data,
                }
            )
        except ValidationError as exc:
            for field_name, field_errors in exc.errors.items():
                target = getattr(form, field_name, None)
                if target is not None:
                    target.errors.extend(field_errors)
        else:
            flash("Your message has been sent. Our team can now review it from the admin inbox.", "success")
            return redirect(url_for("main.contact"))

    return render_template("contact.html", form=form)


@main_bp.get("/about")
def about():
    """Render the product overview page."""
    sections = ScholarshipService.get_homepage_sections()
    return render_template("about.html", sections=sections)
