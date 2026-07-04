from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from app.models import Category, State


class ValidationError(Exception):
    """Raised when incoming data fails business validation."""

    def __init__(self, errors: dict):
        super().__init__("Validation failed.")
        self.errors = errors


class ScholarshipValidator:
    """Validation rules for scholarship payloads."""

    REQUIRED_FIELDS = {
        "scholarship_name",
        "provider_name",
        "scholarship_type",
        "eligibility_description",
        "degree",
        "branch",
        "academic_year",
        "application_link",
        "official_website",
        "application_end_date",
        "description",
        "categories",
        "states",
    }
    UPDATABLE_FIELDS = {
        "scholarship_name",
        "provider_name",
        "scholarship_type",
        "scholarship_amount",
        "eligibility_description",
        "minimum_cgpa",
        "maximum_family_income",
        "gender",
        "degree",
        "branch",
        "academic_year",
        "minority_eligibility",
        "disability_eligibility",
        "hosteller_eligibility",
        "day_scholar_eligibility",
        "required_documents",
        "application_link",
        "official_website",
        "application_start_date",
        "application_end_date",
        "status",
        "is_featured",
        "trending_score",
        "description",
        "benefits",
        "selection_process",
        "is_renewable",
        "categories",
        "states",
    }
    ALLOWED_TYPES = {"government", "private"}
    ALLOWED_GENDERS = {"all", "male", "female", "other"}
    ALLOWED_STATUS = {"draft", "published", "archived"}

    @classmethod
    def validate_create_payload(cls, payload: dict) -> dict:
        """Validate payload for scholarship creation."""
        errors = cls._validate_required_fields(payload)
        clean_payload = cls._normalize_payload(payload, is_partial=False, errors=errors)
        cls._raise_if_errors(errors)
        return clean_payload

    @classmethod
    def validate_update_payload(cls, payload: dict) -> dict:
        """Validate payload for scholarship update."""
        errors = {}
        unsupported_fields = set(payload.keys()) - cls.UPDATABLE_FIELDS
        if unsupported_fields:
            errors["unsupported_fields"] = sorted(unsupported_fields)

        clean_payload = cls._normalize_payload(payload, is_partial=True, errors=errors)
        cls._raise_if_errors(errors)
        return clean_payload

    @classmethod
    def _validate_required_fields(cls, payload: dict) -> dict:
        """Validate missing required fields."""
        errors = {}
        for field_name in sorted(cls.REQUIRED_FIELDS):
            value = payload.get(field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.setdefault(field_name, []).append("This field is required.")
        return errors

    @classmethod
    def _normalize_payload(cls, payload: dict, is_partial: bool, errors: dict) -> dict:
        """Return cleaned payload while collecting validation errors."""
        clean_payload = {}

        for field_name, field_value in payload.items():
            if is_partial and field_name not in cls.UPDATABLE_FIELDS:
                continue

            if field_name in {
                "scholarship_name",
                "provider_name",
                "eligibility_description",
                "degree",
                "branch",
                "academic_year",
                "required_documents",
                "description",
                "benefits",
                "selection_process",
            }:
                clean_payload[field_name] = cls._clean_text(field_name, field_value, errors)
            elif field_name in {"scholarship_type"}:
                clean_payload[field_name] = cls._clean_choice(
                    field_name,
                    field_value,
                    cls.ALLOWED_TYPES,
                    errors,
                )
            elif field_name in {"gender"}:
                clean_payload[field_name] = cls._clean_choice(
                    field_name,
                    field_value,
                    cls.ALLOWED_GENDERS,
                    errors,
                )
            elif field_name in {"status"}:
                clean_payload[field_name] = cls._clean_choice(
                    field_name,
                    field_value,
                    cls.ALLOWED_STATUS,
                    errors,
                )
            elif field_name in {"scholarship_amount", "minimum_cgpa", "maximum_family_income"}:
                clean_payload[field_name] = cls._clean_decimal(field_name, field_value, errors)
            elif field_name in {"application_start_date", "application_end_date"}:
                clean_payload[field_name] = cls._clean_date(field_name, field_value, errors)
            elif field_name in {
                "minority_eligibility",
                "disability_eligibility",
                "hosteller_eligibility",
                "day_scholar_eligibility",
                "is_featured",
                "is_renewable",
            }:
                clean_payload[field_name] = cls._clean_boolean(field_name, field_value, errors)
            elif field_name in {"trending_score"}:
                clean_payload[field_name] = cls._clean_integer(field_name, field_value, errors)
            elif field_name in {"application_link", "official_website"}:
                clean_payload[field_name] = cls._clean_url(field_name, field_value, errors)
            elif field_name == "categories":
                clean_payload[field_name] = cls._clean_categories(field_value, errors)
            elif field_name == "states":
                clean_payload[field_name] = cls._clean_states(field_value, errors)
            else:
                clean_payload[field_name] = field_value

        start_date = clean_payload.get("application_start_date")
        end_date = clean_payload.get("application_end_date")
        if start_date and end_date and start_date > end_date:
            errors.setdefault("application_start_date", []).append(
                "Application start date must be before end date."
            )

        return cls._apply_defaults(clean_payload, is_partial=is_partial)

    @classmethod
    def _apply_defaults(cls, clean_payload: dict, is_partial: bool) -> dict:
        """Fill default values for create payloads."""
        if is_partial:
            return clean_payload

        clean_payload.setdefault("gender", "all")
        clean_payload.setdefault("status", "draft")
        clean_payload.setdefault("minority_eligibility", False)
        clean_payload.setdefault("disability_eligibility", False)
        clean_payload.setdefault("hosteller_eligibility", False)
        clean_payload.setdefault("day_scholar_eligibility", False)
        clean_payload.setdefault("is_featured", False)
        clean_payload.setdefault("trending_score", 0)
        clean_payload.setdefault("is_renewable", False)
        return clean_payload

    @staticmethod
    def _clean_text(field_name: str, field_value, errors: dict) -> str | None:
        """Validate string input."""
        if field_value is None:
            return None
        if not isinstance(field_value, str):
            errors.setdefault(field_name, []).append("Must be a string.")
            return None
        value = field_value.strip()
        if not value:
            errors.setdefault(field_name, []).append("Cannot be blank.")
            return None
        return value

    @staticmethod
    def _clean_choice(field_name: str, field_value, choices: set[str], errors: dict) -> str | None:
        """Validate a limited set of allowed string values."""
        value = ScholarshipValidator._clean_text(field_name, field_value, errors)
        if value is None:
            return None
        normalized = value.lower()
        if normalized not in choices:
            errors.setdefault(field_name, []).append(
                f"Must be one of: {', '.join(sorted(choices))}."
            )
            return None
        return normalized

    @staticmethod
    def _clean_decimal(field_name: str, field_value, errors: dict) -> Decimal | None:
        """Validate decimal input."""
        if field_value in (None, ""):
            return None
        try:
            value = Decimal(str(field_value))
        except (InvalidOperation, ValueError):
            errors.setdefault(field_name, []).append("Must be a valid number.")
            return None
        if value < 0:
            errors.setdefault(field_name, []).append("Must be zero or greater.")
            return None
        return value

    @staticmethod
    def _clean_integer(field_name: str, field_value, errors: dict) -> int | None:
        """Validate integer input."""
        if field_value in (None, ""):
            return None
        try:
            value = int(field_value)
        except (TypeError, ValueError):
            errors.setdefault(field_name, []).append("Must be a valid integer.")
            return None
        if value < 0:
            errors.setdefault(field_name, []).append("Must be zero or greater.")
            return None
        return value

    @staticmethod
    def _clean_boolean(field_name: str, field_value, errors: dict) -> bool | None:
        """Validate boolean input."""
        if isinstance(field_value, bool):
            return field_value
        if isinstance(field_value, str):
            normalized = field_value.strip().lower()
            if normalized in {"true", "1", "yes"}:
                return True
            if normalized in {"false", "0", "no"}:
                return False
        errors.setdefault(field_name, []).append("Must be a boolean.")
        return None

    @staticmethod
    def _clean_date(field_name: str, field_value, errors: dict) -> date | None:
        """Validate ISO date input."""
        if field_value in (None, ""):
            return None
        if not isinstance(field_value, str):
            errors.setdefault(field_name, []).append("Must be an ISO date string.")
            return None
        try:
            return date.fromisoformat(field_value)
        except ValueError:
            errors.setdefault(field_name, []).append("Must use YYYY-MM-DD format.")
            return None

    @staticmethod
    def _clean_url(field_name: str, field_value, errors: dict) -> str | None:
        """Validate URL input."""
        value = ScholarshipValidator._clean_text(field_name, field_value, errors)
        if value is None:
            return None
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.setdefault(field_name, []).append("Must be a valid HTTP or HTTPS URL.")
            return None
        return value

    @staticmethod
    def _clean_categories(field_value, errors: dict) -> list[str]:
        """Validate scholarship category slug list."""
        if not isinstance(field_value, list) or not field_value:
            errors.setdefault("categories", []).append("Must be a non-empty list.")
            return []

        cleaned = []
        for item in field_value:
            if not isinstance(item, str) or not item.strip():
                errors.setdefault("categories", []).append(
                    "Each category must be a non-empty slug string."
                )
                continue
            cleaned.append(item.strip().lower())

        unique_slugs = list(dict.fromkeys(cleaned))
        existing_slugs = {
            category.slug for category in Category.query.filter(Category.slug.in_(unique_slugs)).all()
        }
        missing = sorted(set(unique_slugs) - existing_slugs)
        if missing:
            errors.setdefault("categories", []).append(
                f"Unknown category slugs: {', '.join(missing)}."
            )
        return unique_slugs

    @staticmethod
    def _clean_states(field_value, errors: dict) -> list[str]:
        """Validate scholarship state code list."""
        if not isinstance(field_value, list) or not field_value:
            errors.setdefault("states", []).append("Must be a non-empty list.")
            return []

        cleaned = []
        for item in field_value:
            if not isinstance(item, str) or not item.strip():
                errors.setdefault("states", []).append(
                    "Each state must be a non-empty code string."
                )
                continue
            cleaned.append(item.strip().upper())

        unique_codes = list(dict.fromkeys(cleaned))
        existing_codes = {
            state.code for state in State.query.filter(State.code.in_(unique_codes)).all()
        }
        missing = sorted(set(unique_codes) - existing_codes)
        if missing:
            errors.setdefault("states", []).append(
                f"Unknown state codes: {', '.join(missing)}."
            )
        return unique_codes

    @staticmethod
    def _raise_if_errors(errors: dict) -> None:
        """Raise a typed validation error when collected errors exist."""
        if errors:
            raise ValidationError(errors)


class EligibilityInputValidator:
    """Validation rules for eligibility engine input payloads."""

    REQUIRED_FIELDS = {
        "income",
        "cgpa",
        "category_slug",
        "state_code",
        "gender",
        "degree",
        "branch",
        "academic_year",
        "minority",
        "disability",
        "hosteller",
        "day_scholar",
    }

    @classmethod
    def validate_payload(cls, payload: dict) -> dict:
        """Validate a student eligibility input payload."""
        errors = {}
        clean = {}

        for field_name in sorted(cls.REQUIRED_FIELDS):
            if field_name not in payload:
                errors.setdefault(field_name, []).append("This field is required.")

        clean["income"] = ScholarshipValidator._clean_decimal("income", payload.get("income"), errors)
        clean["cgpa"] = ScholarshipValidator._clean_decimal("cgpa", payload.get("cgpa"), errors)
        clean["category_slug"] = ScholarshipValidator._clean_text(
            "category_slug", payload.get("category_slug"), errors
        )
        clean["state_code"] = ScholarshipValidator._clean_text(
            "state_code", payload.get("state_code"), errors
        )
        clean["gender"] = ScholarshipValidator._clean_choice(
            "gender",
            payload.get("gender"),
            ScholarshipValidator.ALLOWED_GENDERS,
            errors,
        )
        clean["degree"] = ScholarshipValidator._clean_text("degree", payload.get("degree"), errors)
        clean["branch"] = ScholarshipValidator._clean_text("branch", payload.get("branch"), errors)
        clean["academic_year"] = ScholarshipValidator._clean_text(
            "academic_year", payload.get("academic_year"), errors
        )
        clean["minority"] = ScholarshipValidator._clean_boolean("minority", payload.get("minority"), errors)
        clean["disability"] = ScholarshipValidator._clean_boolean(
            "disability", payload.get("disability"), errors
        )
        clean["hosteller"] = ScholarshipValidator._clean_boolean(
            "hosteller", payload.get("hosteller"), errors
        )
        clean["day_scholar"] = ScholarshipValidator._clean_boolean(
            "day_scholar", payload.get("day_scholar"), errors
        )

        if clean["cgpa"] is not None and clean["cgpa"] > Decimal("10"):
            errors.setdefault("cgpa", []).append("CGPA cannot be greater than 10.")

        if clean["category_slug"]:
            clean["category_slug"] = clean["category_slug"].lower()
            category_exists = Category.query.filter_by(
                slug=clean["category_slug"],
                is_active=True,
            ).first()
            if category_exists is None:
                errors.setdefault("category_slug", []).append("Selected category does not exist.")
        if clean["state_code"]:
            clean["state_code"] = clean["state_code"].upper()
            state_exists = State.query.filter_by(code=clean["state_code"], is_active=True).first()
            if state_exists is None:
                errors.setdefault("state_code", []).append("Selected state does not exist.")
        if clean["degree"]:
            clean["degree"] = clean["degree"].strip()
        if clean["branch"]:
            clean["branch"] = clean["branch"].strip()
        if clean["academic_year"]:
            clean["academic_year"] = clean["academic_year"].strip().lower()

        ScholarshipValidator._raise_if_errors(errors)
        return clean
