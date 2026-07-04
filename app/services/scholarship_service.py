from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import Category, Scholarship, ScholarshipCategory, ScholarshipState, State
from app.utils.slug import slugify
from app.utils.validation import ValidationError, ScholarshipValidator


class ScholarshipService:
    """Business logic for scholarship CRUD, filtering, and serialization."""

    @staticmethod
    def list_scholarships(filters: dict, page: int = 1, per_page: int = 10) -> dict:
        """Return paginated scholarships matching the provided filters."""
        page = max(page, 1)
        per_page = min(max(per_page, 1), 50)

        query = Scholarship.query.options(
            selectinload(Scholarship.categories).selectinload(ScholarshipCategory.category),
            selectinload(Scholarship.states).selectinload(ScholarshipState.state),
        )
        query = ScholarshipService._apply_filters(query, filters or {})
        pagination = query.order_by(
            Scholarship.is_featured.desc(),
            Scholarship.application_end_date.asc(),
            Scholarship.created_at.desc(),
        ).paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": [
                ScholarshipService.serialize_scholarship(item) for item in pagination.items
            ],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total_items": pagination.total,
                "total_pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
        }

    @staticmethod
    def get_scholarship_by_id(scholarship_id: int) -> Scholarship | None:
        """Return a scholarship by primary key."""
        return Scholarship.query.options(
            selectinload(Scholarship.categories).selectinload(ScholarshipCategory.category),
            selectinload(Scholarship.states).selectinload(ScholarshipState.state),
        ).filter_by(scholarship_id=scholarship_id).first()

    @staticmethod
    def create_scholarship(payload: dict) -> Scholarship:
        """Validate and persist a scholarship record."""
        clean_payload = ScholarshipValidator.validate_create_payload(payload)
        scholarship = ScholarshipService._build_scholarship(clean_payload)
        db.session.add(scholarship)
        db.session.commit()
        return scholarship

    @staticmethod
    def update_scholarship(scholarship_id: int, payload: dict) -> Scholarship | None:
        """Validate and update an existing scholarship record."""
        scholarship = ScholarshipService.get_scholarship_by_id(scholarship_id)
        if scholarship is None:
            return None

        clean_payload = ScholarshipValidator.validate_update_payload(payload)
        ScholarshipService._apply_scholarship_updates(scholarship, clean_payload)
        db.session.commit()
        return scholarship

    @staticmethod
    def delete_scholarship(scholarship_id: int) -> bool:
        """Delete an existing scholarship."""
        scholarship = Scholarship.query.filter_by(scholarship_id=scholarship_id).first()
        if scholarship is None:
            return False

        db.session.delete(scholarship)
        db.session.commit()
        return True

    @staticmethod
    def list_for_admin(limit: int = 20) -> list[Scholarship]:
        """Return recent scholarships for admin management screens."""
        return (
            Scholarship.query.order_by(
                Scholarship.updated_at.desc(),
                Scholarship.created_at.desc(),
            )
            .limit(max(limit, 1))
            .all()
        )

    @staticmethod
    def serialize_scholarship(scholarship: Scholarship) -> dict:
        """Convert scholarship model data into JSON-friendly output."""
        return {
            "scholarship_id": scholarship.scholarship_id,
            "scholarship_name": scholarship.scholarship_name,
            "slug": scholarship.slug,
            "provider_name": scholarship.provider_name,
            "scholarship_type": scholarship.scholarship_type,
            "scholarship_amount": ScholarshipService._decimal_to_float(
                scholarship.scholarship_amount
            ),
            "eligibility_description": scholarship.eligibility_description,
            "minimum_cgpa": ScholarshipService._decimal_to_float(scholarship.minimum_cgpa),
            "maximum_family_income": ScholarshipService._decimal_to_float(
                scholarship.maximum_family_income
            ),
            "gender": scholarship.gender,
            "degree": scholarship.degree,
            "branch": scholarship.branch,
            "academic_year": scholarship.academic_year,
            "minority_eligibility": scholarship.minority_eligibility,
            "disability_eligibility": scholarship.disability_eligibility,
            "hosteller_eligibility": scholarship.hosteller_eligibility,
            "day_scholar_eligibility": scholarship.day_scholar_eligibility,
            "required_documents": scholarship.required_documents,
            "application_link": scholarship.application_link,
            "official_website": scholarship.official_website,
            "application_start_date": ScholarshipService._serialize_date(
                scholarship.application_start_date
            ),
            "application_end_date": ScholarshipService._serialize_date(
                scholarship.application_end_date
            ),
            "status": scholarship.status,
            "is_featured": scholarship.is_featured,
            "trending_score": scholarship.trending_score,
            "description": scholarship.description,
            "benefits": scholarship.benefits,
            "selection_process": scholarship.selection_process,
            "is_renewable": scholarship.is_renewable,
            "view_count": scholarship.view_count,
            "last_verified_at": ScholarshipService._serialize_datetime(
                scholarship.last_verified_at
            ),
            "categories": [link.category.slug for link in scholarship.categories],
            "states": [link.state.code for link in scholarship.states],
            "created_at": ScholarshipService._serialize_datetime(scholarship.created_at),
            "updated_at": ScholarshipService._serialize_datetime(scholarship.updated_at),
        }

    @staticmethod
    def _apply_filters(query, filters: dict):
        """Apply supported filters for scholarship discovery."""
        keyword = filters.get("keyword")
        if keyword:
            search_term = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    Scholarship.scholarship_name.ilike(search_term),
                    Scholarship.provider_name.ilike(search_term),
                    Scholarship.description.ilike(search_term),
                )
            )

        scholarship_type = filters.get("scholarship_type")
        if scholarship_type:
            query = query.filter(Scholarship.scholarship_type == scholarship_type.lower())

        state_code = filters.get("state_code")
        if state_code:
            query = query.join(Scholarship.states).join(ScholarshipState.state).filter(
                State.code == state_code.upper()
            )

        category_slug = filters.get("category_slug")
        if category_slug:
            query = query.join(Scholarship.categories).join(ScholarshipCategory.category).filter(
                Category.slug == category_slug.lower()
            )

        gender = filters.get("gender")
        if gender:
            normalized_gender = gender.lower()
            query = query.filter(
                Scholarship.gender.in_(["all", normalized_gender])
            )

        degree = filters.get("degree")
        if degree:
            query = query.filter(Scholarship.degree == degree)

        branch = filters.get("branch")
        if branch:
            query = query.filter(Scholarship.branch == branch)

        academic_year = filters.get("academic_year")
        if academic_year:
            query = query.filter(Scholarship.academic_year == academic_year)

        max_income = filters.get("max_income")
        if max_income is not None:
            query = query.filter(
                or_(
                    Scholarship.maximum_family_income.is_(None),
                    Scholarship.maximum_family_income >= max_income,
                )
            )

        min_cgpa = filters.get("min_cgpa")
        if min_cgpa is not None:
            query = query.filter(
                or_(
                    Scholarship.minimum_cgpa.is_(None),
                    Scholarship.minimum_cgpa <= min_cgpa,
                )
            )

        is_featured = filters.get("is_featured")
        if is_featured is not None:
            normalized_flag = str(is_featured).strip().lower()
            if normalized_flag in {"true", "1", "yes"}:
                query = query.filter(Scholarship.is_featured.is_(True))
            elif normalized_flag in {"false", "0", "no"}:
                query = query.filter(Scholarship.is_featured.is_(False))

        deadline_within_days = filters.get("deadline_within_days")
        if deadline_within_days is not None and deadline_within_days >= 0:
            cutoff_date = date.today() + timedelta(days=deadline_within_days)
            query = query.filter(Scholarship.application_end_date <= cutoff_date)

        status = filters.get("status")
        if status:
            query = query.filter(Scholarship.status == status.lower())

        return query.distinct()

    @staticmethod
    def _build_scholarship(clean_payload: dict) -> Scholarship:
        """Create a scholarship model from validated payload."""
        scholarship = Scholarship(
            scholarship_name=clean_payload["scholarship_name"],
            slug=ScholarshipService._generate_unique_slug(clean_payload["scholarship_name"]),
            provider_name=clean_payload["provider_name"],
            scholarship_type=clean_payload["scholarship_type"],
            scholarship_amount=clean_payload.get("scholarship_amount"),
            eligibility_description=clean_payload["eligibility_description"],
            minimum_cgpa=clean_payload.get("minimum_cgpa"),
            maximum_family_income=clean_payload.get("maximum_family_income"),
            gender=clean_payload["gender"],
            degree=clean_payload["degree"],
            branch=clean_payload["branch"],
            academic_year=clean_payload["academic_year"],
            minority_eligibility=clean_payload["minority_eligibility"],
            disability_eligibility=clean_payload["disability_eligibility"],
            hosteller_eligibility=clean_payload["hosteller_eligibility"],
            day_scholar_eligibility=clean_payload["day_scholar_eligibility"],
            required_documents=clean_payload.get("required_documents"),
            application_link=clean_payload["application_link"],
            official_website=clean_payload["official_website"],
            application_start_date=clean_payload.get("application_start_date"),
            application_end_date=clean_payload["application_end_date"],
            status=clean_payload["status"],
            is_featured=clean_payload["is_featured"],
            trending_score=clean_payload["trending_score"],
            description=clean_payload["description"],
            benefits=clean_payload.get("benefits"),
            selection_process=clean_payload.get("selection_process"),
            is_renewable=clean_payload["is_renewable"],
        )
        ScholarshipService._sync_categories(scholarship, clean_payload["categories"])
        ScholarshipService._sync_states(scholarship, clean_payload["states"])
        return scholarship

    @staticmethod
    def _apply_scholarship_updates(scholarship: Scholarship, clean_payload: dict) -> None:
        """Apply validated payload to an existing scholarship model."""
        for field_name in ScholarshipValidator.UPDATABLE_FIELDS:
            if field_name not in clean_payload:
                continue

            if field_name == "scholarship_name":
                scholarship.scholarship_name = clean_payload[field_name]
                scholarship.slug = ScholarshipService._generate_unique_slug(
                    clean_payload[field_name],
                    scholarship_id=scholarship.scholarship_id,
                )
                continue

            if field_name == "categories":
                ScholarshipService._sync_categories(scholarship, clean_payload[field_name])
                continue

            if field_name == "states":
                ScholarshipService._sync_states(scholarship, clean_payload[field_name])
                continue

            setattr(scholarship, field_name, clean_payload[field_name])

    @staticmethod
    def _sync_categories(scholarship: Scholarship, category_slugs: list[str]) -> None:
        """Replace scholarship category mappings."""
        categories = Category.query.filter(Category.slug.in_(category_slugs)).all()
        category_map = {category.slug: category for category in categories}

        scholarship.categories.clear()
        for slug in category_slugs:
            scholarship.categories.append(
                ScholarshipCategory(category=category_map[slug])
            )

    @staticmethod
    def _sync_states(scholarship: Scholarship, state_codes: list[str]) -> None:
        """Replace scholarship state mappings."""
        states = State.query.filter(State.code.in_(state_codes)).all()
        state_map = {state.code: state for state in states}

        scholarship.states.clear()
        for code in state_codes:
            scholarship.states.append(
                ScholarshipState(state=state_map[code])
            )

    @staticmethod
    def _generate_unique_slug(name: str, scholarship_id: int | None = None) -> str:
        """Generate a unique slug for scholarship records."""
        base_slug = slugify(name)
        candidate = base_slug
        counter = 2

        while True:
            existing = Scholarship.query.filter_by(slug=candidate).first()
            if existing is None or existing.scholarship_id == scholarship_id:
                return candidate
            candidate = f"{base_slug}-{counter}"
            counter += 1

    @staticmethod
    def _decimal_to_float(value: Decimal | None) -> float | None:
        """Convert Decimal values into float for JSON responses."""
        if value is None:
            return None
        return float(value)

    @staticmethod
    def _serialize_date(value: date | None) -> str | None:
        """Serialize date values in ISO format."""
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def _serialize_datetime(value) -> str | None:
        """Serialize datetime values in ISO format."""
        if value is None:
            return None
        return value.isoformat()
