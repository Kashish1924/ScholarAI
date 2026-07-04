from app.models import Scholarship


def scholarship_to_form_payload(scholarship: Scholarship) -> dict:
    """Convert a scholarship model into form-friendly values."""
    return {
        "scholarship_name": scholarship.scholarship_name,
        "provider_name": scholarship.provider_name,
        "scholarship_type": scholarship.scholarship_type,
        "scholarship_amount": _value_or_empty(scholarship.scholarship_amount),
        "eligibility_description": scholarship.eligibility_description,
        "minimum_cgpa": _value_or_empty(scholarship.minimum_cgpa),
        "maximum_family_income": _value_or_empty(scholarship.maximum_family_income),
        "gender": scholarship.gender,
        "degree": scholarship.degree,
        "branch": scholarship.branch,
        "academic_year": scholarship.academic_year,
        "minority_eligibility": scholarship.minority_eligibility,
        "disability_eligibility": scholarship.disability_eligibility,
        "hosteller_eligibility": scholarship.hosteller_eligibility,
        "day_scholar_eligibility": scholarship.day_scholar_eligibility,
        "required_documents": scholarship.required_documents or "",
        "application_link": scholarship.application_link,
        "official_website": scholarship.official_website,
        "application_start_date": _value_or_empty(scholarship.application_start_date),
        "application_end_date": _value_or_empty(scholarship.application_end_date),
        "status": scholarship.status,
        "is_featured": scholarship.is_featured,
        "trending_score": scholarship.trending_score,
        "description": scholarship.description,
        "benefits": scholarship.benefits or "",
        "selection_process": scholarship.selection_process or "",
        "is_renewable": scholarship.is_renewable,
        "categories": ", ".join(link.category.slug for link in scholarship.categories),
        "states": ", ".join(link.state.code for link in scholarship.states),
    }


def build_scholarship_payload_from_form(form) -> dict:
    """Convert form data into service payload."""
    return {
        "scholarship_name": form.scholarship_name.data,
        "provider_name": form.provider_name.data,
        "scholarship_type": form.scholarship_type.data,
        "scholarship_amount": form.scholarship_amount.data,
        "eligibility_description": form.eligibility_description.data,
        "minimum_cgpa": form.minimum_cgpa.data,
        "maximum_family_income": form.maximum_family_income.data,
        "gender": form.gender.data,
        "degree": form.degree.data,
        "branch": form.branch.data,
        "academic_year": form.academic_year.data,
        "minority_eligibility": form.minority_eligibility.data,
        "disability_eligibility": form.disability_eligibility.data,
        "hosteller_eligibility": form.hosteller_eligibility.data,
        "day_scholar_eligibility": form.day_scholar_eligibility.data,
        "required_documents": form.required_documents.data,
        "application_link": form.application_link.data,
        "official_website": form.official_website.data,
        "application_start_date": form.application_start_date.data,
        "application_end_date": form.application_end_date.data,
        "status": form.status.data,
        "is_featured": form.is_featured.data,
        "trending_score": form.trending_score.data or 0,
        "description": form.description.data,
        "benefits": form.benefits.data,
        "selection_process": form.selection_process.data,
        "is_renewable": form.is_renewable.data,
        "categories": _split_csv(form.categories.data),
        "states": _split_csv(form.states.data, uppercase=True),
    }


def _split_csv(value: str, uppercase: bool = False) -> list[str]:
    """Split comma-separated text into clean list values."""
    items = []
    for part in (value or "").split(","):
        cleaned = part.strip()
        if not cleaned:
            continue
        items.append(cleaned.upper() if uppercase else cleaned.lower())
    return items


def _value_or_empty(value):
    """Return a form-friendly string value."""
    if value is None:
        return ""
    return str(value)
