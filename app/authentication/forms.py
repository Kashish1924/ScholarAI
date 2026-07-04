from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, URL


class AdminLoginForm(FlaskForm):
    """Admin login form."""

    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class ScholarshipForm(FlaskForm):
    """Admin scholarship create and edit form."""

    scholarship_name = StringField("Scholarship Name", validators=[DataRequired(), Length(max=255)])
    provider_name = StringField("Provider Name", validators=[DataRequired(), Length(max=255)])
    scholarship_type = SelectField(
        "Scholarship Type",
        choices=[("government", "Government"), ("private", "Private")],
        validators=[DataRequired()],
    )
    scholarship_amount = StringField("Scholarship Amount", validators=[Optional(), Length(max=50)])
    eligibility_description = TextAreaField("Eligibility Description", validators=[DataRequired()])
    minimum_cgpa = StringField("Minimum CGPA", validators=[Optional(), Length(max=10)])
    maximum_family_income = StringField("Maximum Family Income", validators=[Optional(), Length(max=20)])
    gender = SelectField(
        "Gender",
        choices=[
            ("all", "All"),
            ("female", "Female"),
            ("male", "Male"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    degree = StringField("Degree", validators=[DataRequired(), Length(max=100)])
    branch = StringField("Branch", validators=[DataRequired(), Length(max=100)])
    academic_year = SelectField(
        "Academic Year",
        choices=[
            ("1", "1st Year"),
            ("2", "2nd Year"),
            ("3", "3rd Year"),
            ("4", "4th Year"),
            ("all", "All Years"),
        ],
        validators=[DataRequired()],
    )
    minority_eligibility = BooleanField("Minority Eligibility")
    disability_eligibility = BooleanField("Disability Eligibility")
    hosteller_eligibility = BooleanField("Hosteller Eligibility")
    day_scholar_eligibility = BooleanField("Day Scholar Eligibility")
    required_documents = TextAreaField("Required Documents", validators=[Optional()])
    application_link = StringField("Application Link", validators=[DataRequired(), URL(), Length(max=500)])
    official_website = StringField("Official Website", validators=[DataRequired(), URL(), Length(max=500)])
    application_start_date = StringField("Application Start Date", validators=[Optional(), Length(max=10)])
    application_end_date = StringField("Application End Date", validators=[DataRequired(), Length(max=10)])
    status = SelectField(
        "Status",
        choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
        validators=[DataRequired()],
    )
    is_featured = BooleanField("Featured Scholarship")
    trending_score = StringField("Trending Score", validators=[Optional(), Length(max=10)])
    description = TextAreaField("Description", validators=[DataRequired()])
    benefits = TextAreaField("Benefits", validators=[Optional()])
    selection_process = TextAreaField("Selection Process", validators=[Optional()])
    is_renewable = BooleanField("Renewable")
    categories = StringField(
        "Categories",
        validators=[DataRequired()],
        description="Comma-separated category slugs, for example: obc, general",
    )
    states = StringField(
        "States",
        validators=[DataRequired()],
        description="Comma-separated state codes, for example: DL, MH",
    )
    submit = SubmitField("Save Scholarship")


class NewsForm(FlaskForm):
    """Admin news create and edit form."""

    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    summary = TextAreaField("Summary", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    source_url = StringField("Source URL", validators=[Optional(), URL(), Length(max=500)])
    image_url = StringField("Image URL", validators=[Optional(), URL(), Length(max=500)])
    priority = IntegerField("Priority", validators=[Optional()])
    is_published = BooleanField("Published")
    related_scholarship_id = IntegerField("Related Scholarship ID", validators=[Optional()])
    submit = SubmitField("Save News")


class FAQForm(FlaskForm):
    """Admin FAQ create and edit form."""

    question = StringField("Question", validators=[DataRequired(), Length(max=255)])
    answer = TextAreaField("Answer", validators=[DataRequired()])
    display_order = IntegerField("Display Order", validators=[Optional()])
    is_published = BooleanField("Published")
    submit = SubmitField("Save FAQ")


class NotificationForm(FlaskForm):
    """Admin notification create and edit form."""

    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    message = TextAreaField("Message", validators=[DataRequired()])
    notification_type = SelectField(
        "Notification Type",
        choices=[
            ("general", "General"),
            ("reminder", "Reminder"),
            ("alert", "Alert"),
        ],
        validators=[DataRequired()],
    )
    audience_type = SelectField(
        "Audience Type",
        choices=[
            ("all", "All"),
            ("student", "Student"),
            ("admin", "Admin"),
        ],
        validators=[DataRequired()],
    )
    is_active = BooleanField("Active")
    starts_at = StringField("Starts At", validators=[Optional(), Length(max=25)])
    ends_at = StringField("Ends At", validators=[Optional(), Length(max=25)])
    related_scholarship_id = IntegerField("Related Scholarship ID", validators=[Optional()])
    submit = SubmitField("Save Notification")


class CSVUploadForm(FlaskForm):
    """Admin CSV import form."""

    csv_file = FileField("Scholarship CSV", validators=[DataRequired()])
    submit = SubmitField("Import CSV")


class BulkScholarshipActionForm(FlaskForm):
    """Admin bulk scholarship action form."""

    action = SelectField(
        "Bulk Action",
        choices=[
            ("publish", "Publish"),
            ("archive", "Archive"),
            ("feature", "Mark as Featured"),
            ("unfeature", "Remove Featured"),
            ("delete", "Delete"),
        ],
        validators=[DataRequired()],
    )
    selected_ids = StringField("Selected IDs", validators=[DataRequired()])
    submit = SubmitField("Apply")


class ContactForm(FlaskForm):
    """Public contact form."""

    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=255)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=3000)])
    submit = SubmitField("Send Message")


class ContactResolutionForm(FlaskForm):
    """Admin contact message resolution form."""

    submit = SubmitField("Mark as Resolved")
