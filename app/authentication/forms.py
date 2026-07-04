from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
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
