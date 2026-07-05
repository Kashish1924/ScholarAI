import csv
import io
import re
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

    CSV_FIELDNAMES = [
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
    ]

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
    def get_scholarship_by_slug(slug: str) -> Scholarship | None:
        """Return a scholarship by slug."""
        return Scholarship.query.options(
            selectinload(Scholarship.categories).selectinload(ScholarshipCategory.category),
            selectinload(Scholarship.states).selectinload(ScholarshipState.state),
        ).filter_by(slug=slug).first()

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
    def bulk_apply_action(action: str, scholarship_ids: list[int]) -> dict:
        """Apply supported bulk actions to selected scholarships."""
        if not scholarship_ids:
            raise ValidationError({"selected_ids": ["Select at least one scholarship."]})

        scholarships = Scholarship.query.filter(
            Scholarship.scholarship_id.in_(scholarship_ids)
        ).all()
        if not scholarships:
            raise ValidationError({"selected_ids": ["No matching scholarships were found."]})

        affected_ids = [item.scholarship_id for item in scholarships]
        if action == "publish":
            for item in scholarships:
                item.status = "published"
        elif action == "archive":
            for item in scholarships:
                item.status = "archived"
        elif action == "feature":
            for item in scholarships:
                item.is_featured = True
        elif action == "unfeature":
            for item in scholarships:
                item.is_featured = False
        elif action == "delete":
            for item in scholarships:
                db.session.delete(item)
        else:
            raise ValidationError({"action": ["Unsupported bulk action."]})

        db.session.commit()
        return {
            "action": action,
            "affected_ids": affected_ids,
            "affected_count": len(affected_ids),
        }

    @staticmethod
    def import_scholarships_from_csv(file_storage) -> dict:
        """Import scholarship rows from a CSV file with row-level validation."""
        if file_storage is None or not file_storage.filename:
            raise ValidationError({"csv_file": ["A CSV file is required."]})
        if not file_storage.filename.lower().endswith(".csv"):
            raise ValidationError({"csv_file": ["Only CSV files are supported."]})

        try:
            raw_text = file_storage.stream.read().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValidationError({"csv_file": ["CSV must be UTF-8 encoded."]}) from exc

        reader = csv.DictReader(io.StringIO(raw_text))
        if reader.fieldnames is None:
            raise ValidationError({"csv_file": ["CSV file is empty or missing headers."]})

        missing_headers = [
            field_name for field_name in ScholarshipService.CSV_FIELDNAMES
            if field_name not in reader.fieldnames
        ]
        if missing_headers:
            raise ValidationError(
                {"csv_file": [f"Missing required headers: {', '.join(missing_headers)}."]}
            )

        imported_count = 0
        row_errors = []

        for row_number, row in enumerate(reader, start=2):
            payload = ScholarshipService._csv_row_to_payload(row)
            try:
                scholarship = ScholarshipService._build_scholarship(
                    ScholarshipValidator.validate_create_payload(payload)
                )
            except ValidationError as exc:
                row_errors.append(
                    {
                        "row": row_number,
                        "errors": exc.errors,
                    }
                )
                continue

            db.session.add(scholarship)
            imported_count += 1

        db.session.commit()
        return {
            "imported_count": imported_count,
            "rejected_count": len(row_errors),
            "errors": row_errors,
        }

    @staticmethod
    def export_scholarships_to_csv() -> str:
        """Export scholarship records to CSV text."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=ScholarshipService.CSV_FIELDNAMES)
        writer.writeheader()

        scholarships = Scholarship.query.options(
            selectinload(Scholarship.categories).selectinload(ScholarshipCategory.category),
            selectinload(Scholarship.states).selectinload(ScholarshipState.state),
        ).order_by(Scholarship.created_at.desc()).all()

        for item in scholarships:
            writer.writerow(
                {
                    "scholarship_name": item.scholarship_name,
                    "provider_name": item.provider_name,
                    "scholarship_type": item.scholarship_type,
                    "scholarship_amount": item.scholarship_amount or "",
                    "eligibility_description": item.eligibility_description,
                    "minimum_cgpa": item.minimum_cgpa or "",
                    "maximum_family_income": item.maximum_family_income or "",
                    "gender": item.gender,
                    "degree": item.degree,
                    "branch": item.branch,
                    "academic_year": item.academic_year,
                    "minority_eligibility": item.minority_eligibility,
                    "disability_eligibility": item.disability_eligibility,
                    "hosteller_eligibility": item.hosteller_eligibility,
                    "day_scholar_eligibility": item.day_scholar_eligibility,
                    "required_documents": item.required_documents or "",
                    "application_link": item.application_link,
                    "official_website": item.official_website,
                    "application_start_date": item.application_start_date.isoformat() if item.application_start_date else "",
                    "application_end_date": item.application_end_date.isoformat() if item.application_end_date else "",
                    "status": item.status,
                    "is_featured": item.is_featured,
                    "trending_score": item.trending_score,
                    "description": item.description,
                    "benefits": item.benefits or "",
                    "selection_process": item.selection_process or "",
                    "is_renewable": item.is_renewable,
                    "categories": ", ".join(link.category.slug for link in item.categories),
                    "states": ", ".join(link.state.code for link in item.states),
                }
            )

        return output.getvalue()

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
    def get_homepage_sections() -> dict:
        """Return featured homepage scholarship sections."""
        featured = (
            Scholarship.query.filter_by(status="published", is_featured=True)
            .order_by(Scholarship.trending_score.desc(), Scholarship.created_at.desc())
            .limit(4)
            .all()
        )
        trending = (
            Scholarship.query.filter_by(status="published")
            .order_by(Scholarship.trending_score.desc(), Scholarship.view_count.desc())
            .limit(4)
            .all()
        )
        closing_soon = (
            Scholarship.query.filter(
                Scholarship.status == "published",
                Scholarship.application_end_date >= date.today(),
            )
            .order_by(Scholarship.application_end_date.asc())
            .limit(4)
            .all()
        )
        latest = (
            Scholarship.query.filter_by(status="published")
            .order_by(Scholarship.created_at.desc())
            .limit(4)
            .all()
        )

        return {
            "featured": [ScholarshipService.serialize_scholarship(item) for item in featured],
            "trending": [ScholarshipService.serialize_scholarship(item) for item in trending],
            "closing_soon": [ScholarshipService.serialize_scholarship(item) for item in closing_soon],
            "latest": [ScholarshipService.serialize_scholarship(item) for item in latest],
            "stats": {
                "published_count": Scholarship.query.filter_by(status="published").count(),
                "government_count": Scholarship.query.filter_by(
                    status="published",
                    scholarship_type="government",
                ).count(),
                "private_count": Scholarship.query.filter_by(
                    status="published",
                    scholarship_type="private",
                ).count(),
                "featured_count": Scholarship.query.filter_by(
                    status="published",
                    is_featured=True,
                ).count(),
            },
        }

    @staticmethod
    def get_comparison_data(scholarship_ids: list[int]) -> list[dict]:
        """Return serialized scholarships for comparison."""
        if not scholarship_ids:
            return []

        scholarships = (
            Scholarship.query.options(
                selectinload(Scholarship.categories).selectinload(ScholarshipCategory.category),
                selectinload(Scholarship.states).selectinload(ScholarshipState.state),
            )
            .filter(Scholarship.scholarship_id.in_(scholarship_ids))
            .limit(3)
            .all()
        )
        order_map = {item_id: index for index, item_id in enumerate(scholarship_ids)}
        scholarships.sort(key=lambda item: order_map.get(item.scholarship_id, 999))
        return [ScholarshipService.serialize_scholarship(item) for item in scholarships]

    @staticmethod
    def get_filter_options() -> dict:
        """Return lookup and suggestion values for filter UIs."""
        return {
            "scholarship_types": ["government", "private"],
            "genders": ["all", "female", "male", "other"],
            "degrees": sorted(
                {
                    item[0]
                    for item in Scholarship.query.with_entities(Scholarship.degree)
                    .filter(Scholarship.degree.isnot(None))
                    .distinct()
                    .all()
                    if item[0]
                }
            ),
            "branches": sorted(
                {
                    item[0]
                    for item in Scholarship.query.with_entities(Scholarship.branch)
                    .filter(Scholarship.branch.isnot(None))
                    .distinct()
                    .all()
                    if item[0]
                }
            ),
            "academic_years": sorted(
                {
                    item[0]
                    for item in Scholarship.query.with_entities(Scholarship.academic_year)
                    .filter(Scholarship.academic_year.isnot(None))
                    .distinct()
                    .all()
                    if item[0]
                }
            ),
            "categories": [
                {"category_id": item.category_id, "name": item.name, "slug": item.slug}
                for item in Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()
            ],
            "states": [
                {"state_id": item.state_id, "name": item.name, "code": item.code}
                for item in State.query.filter_by(is_active=True).order_by(State.name.asc()).all()
            ],
        }

    @staticmethod
    def get_search_suggestions(query_text: str, limit: int = 8) -> list[dict]:
        """Return lightweight search suggestions for the public search bar."""
        normalized_query = (query_text or "").strip()
        if len(normalized_query) < 2:
            return []

        search_term = f"%{normalized_query}%"
        suggestions = []

        for scholarship in (
            Scholarship.query.filter(
                or_(
                    Scholarship.scholarship_name.ilike(search_term),
                    Scholarship.provider_name.ilike(search_term),
                    Scholarship.branch.ilike(search_term),
                    Scholarship.degree.ilike(search_term),
                )
            )
            .order_by(Scholarship.is_featured.desc(), Scholarship.trending_score.desc())
            .limit(limit)
            .all()
        ):
            suggestions.append(
                {
                    "type": "scholarship",
                    "label": scholarship.scholarship_name,
                    "meta": scholarship.provider_name,
                    "slug": scholarship.slug,
                }
            )

        for category in (
            Category.query.filter(Category.name.ilike(search_term))
            .order_by(Category.name.asc())
            .limit(3)
            .all()
        ):
            suggestions.append(
                {
                    "type": "category",
                    "label": category.name,
                    "meta": category.slug,
                    "slug": None,
                }
            )

        for state in (
            State.query.filter(State.name.ilike(search_term))
            .order_by(State.name.asc())
            .limit(3)
            .all()
        ):
            suggestions.append(
                {
                    "type": "state",
                    "label": state.name,
                    "meta": state.code,
                    "slug": None,
                }
            )

        unique_items = []
        seen = set()
        for item in suggestions:
            marker = (item["type"], item["label"], item["meta"])
            if marker in seen:
                continue
            seen.add(marker)
            unique_items.append(item)
            if len(unique_items) >= limit:
                break
        return unique_items

    @staticmethod
    def interpret_natural_language_query(query_text: str) -> dict:
        """Extract practical filters from a free-text scholarship query."""
        raw_query = (query_text or "").strip()
        normalized_query = raw_query.lower()
        filters = {}
        signals = []

        if not raw_query:
            return {
                "input": raw_query,
                "filters": filters,
                "signals": signals,
                "summary": "Enter a longer scholarship request to interpret it.",
            }

        income_match = re.search(r"(?:under|below|less than)\s+(\d+(?:\.\d+)?)\s*(lakh|lac|lakhs)?", normalized_query)
        if income_match:
            income_value = float(income_match.group(1))
            if income_match.group(2):
                income_value *= 100000
            filters["max_income"] = income_value
            signals.append(f"Family income preference under {int(income_value)} detected.")

        if "girls" in normalized_query or "female" in normalized_query:
            filters["gender"] = "female"
            signals.append("Female-only preference detected.")
        elif "boys" in normalized_query or "male" in normalized_query:
            filters["gender"] = "male"
            signals.append("Male-only preference detected.")

        if "government" in normalized_query:
            filters["scholarship_type"] = "government"
            signals.append("Government scholarship preference detected.")
        elif "private" in normalized_query:
            filters["scholarship_type"] = "private"
            signals.append("Private scholarship preference detected.")

        if "this week" in normalized_query:
            filters["deadline_within_days"] = 7
            signals.append("Deadline window within 7 days detected.")
        elif "this month" in normalized_query:
            filters["deadline_within_days"] = 30
            signals.append("Deadline window within 30 days detected.")

        categories = Category.query.filter_by(is_active=True).all()
        for category in categories:
            if category.slug.lower() in normalized_query or category.name.lower() in normalized_query:
                filters["category_slug"] = category.slug
                signals.append(f"Category match detected for {category.name}.")
                break

        states = State.query.filter_by(is_active=True).all()
        for state in states:
            if state.name.lower() in normalized_query or state.code.lower() in normalized_query.split():
                filters["state_code"] = state.code
                signals.append(f"State match detected for {state.name}.")
                break

        branch_terms = ["cse", "ece", "eee", "me", "civil", "it", "mechanical"]
        for branch in branch_terms:
            if branch in normalized_query:
                filters["branch"] = branch.upper() if len(branch) <= 3 else branch.title()
                signals.append(f"Branch match detected for {filters['branch']}.")
                break

        if "b.tech" in normalized_query or "btech" in normalized_query:
            filters["degree"] = "B.Tech"
            signals.append("Degree match detected for B.Tech.")

        year_match = re.search(r"\b([1-4])(st|nd|rd|th)?\s+year\b", normalized_query)
        if year_match:
            filters["academic_year"] = year_match.group(1)
            signals.append(f"Academic year {year_match.group(1)} detected.")

        summary = (
            "No structured filters were confidently extracted, so the query will behave like a keyword search."
            if not signals
            else "Structured hints were extracted from the natural-language query to improve search relevance."
        )
        return {
            "input": raw_query,
            "filters": filters,
            "signals": signals,
            "summary": summary,
        }

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
        if "scholarship_name" in clean_payload:
            scholarship.scholarship_name = clean_payload["scholarship_name"]
            scholarship.slug = ScholarshipService._generate_unique_slug(
                clean_payload["scholarship_name"],
                scholarship_id=scholarship.scholarship_id,
            )

        deferred_fields = {"scholarship_name", "categories", "states"}
        for field_name, field_value in clean_payload.items():
            if field_name in deferred_fields:
                continue
            setattr(scholarship, field_name, field_value)

        if "categories" in clean_payload:
            ScholarshipService._sync_categories(scholarship, clean_payload["categories"])

        if "states" in clean_payload:
            ScholarshipService._sync_states(scholarship, clean_payload["states"])

    @staticmethod
    def _sync_categories(scholarship: Scholarship, category_slugs: list[str]) -> None:
        """Replace scholarship category mappings."""
        with db.session.no_autoflush:
            categories = Category.query.filter(Category.slug.in_(category_slugs)).all()
        category_map = {category.slug: category for category in categories}
        if scholarship.scholarship_id is not None:
            db.session.query(ScholarshipCategory).filter_by(
                scholarship_id=scholarship.scholarship_id
            ).delete(synchronize_session=False)
            db.session.flush()
        scholarship.categories = []
        for slug in category_slugs:
            scholarship.categories.append(
                ScholarshipCategory(category=category_map[slug], scholarship=scholarship)
            )

    @staticmethod
    def _sync_states(scholarship: Scholarship, state_codes: list[str]) -> None:
        """Replace scholarship state mappings."""
        with db.session.no_autoflush:
            states = State.query.filter(State.code.in_(state_codes)).all()
        state_map = {state.code: state for state in states}
        if scholarship.scholarship_id is not None:
            db.session.query(ScholarshipState).filter_by(
                scholarship_id=scholarship.scholarship_id
            ).delete(synchronize_session=False)
            db.session.flush()
        scholarship.states = []
        for code in state_codes:
            scholarship.states.append(
                ScholarshipState(state=state_map[code], scholarship=scholarship)
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
    def _csv_row_to_payload(row: dict) -> dict:
        """Normalize a CSV row into scholarship payload format."""
        return {
            "scholarship_name": (row.get("scholarship_name") or "").strip(),
            "provider_name": (row.get("provider_name") or "").strip(),
            "scholarship_type": (row.get("scholarship_type") or "").strip(),
            "scholarship_amount": (row.get("scholarship_amount") or "").strip(),
            "eligibility_description": (row.get("eligibility_description") or "").strip(),
            "minimum_cgpa": (row.get("minimum_cgpa") or "").strip(),
            "maximum_family_income": (row.get("maximum_family_income") or "").strip(),
            "gender": (row.get("gender") or "").strip() or "all",
            "degree": (row.get("degree") or "").strip(),
            "branch": (row.get("branch") or "").strip(),
            "academic_year": (row.get("academic_year") or "").strip(),
            "minority_eligibility": (row.get("minority_eligibility") or "").strip() or "false",
            "disability_eligibility": (row.get("disability_eligibility") or "").strip() or "false",
            "hosteller_eligibility": (row.get("hosteller_eligibility") or "").strip() or "false",
            "day_scholar_eligibility": (row.get("day_scholar_eligibility") or "").strip() or "false",
            "required_documents": (row.get("required_documents") or "").strip(),
            "application_link": (row.get("application_link") or "").strip(),
            "official_website": (row.get("official_website") or "").strip(),
            "application_start_date": (row.get("application_start_date") or "").strip(),
            "application_end_date": (row.get("application_end_date") or "").strip(),
            "status": (row.get("status") or "").strip() or "draft",
            "is_featured": (row.get("is_featured") or "").strip() or "false",
            "trending_score": (row.get("trending_score") or "").strip() or "0",
            "description": (row.get("description") or "").strip(),
            "benefits": (row.get("benefits") or "").strip(),
            "selection_process": (row.get("selection_process") or "").strip(),
            "is_renewable": (row.get("is_renewable") or "").strip() or "false",
            "categories": ScholarshipService._csv_list(row.get("categories")),
            "states": ScholarshipService._csv_list(row.get("states"), uppercase=True),
        }

    @staticmethod
    def _csv_list(value, uppercase: bool = False) -> list[str]:
        """Convert comma-separated CSV text to normalized list values."""
        if value in (None, ""):
            return []
        items = []
        for part in str(value).split(","):
            cleaned = part.strip()
            if not cleaned:
                continue
            items.append(cleaned.upper() if uppercase else cleaned.lower())
        return items

    @staticmethod
    def _serialize_datetime(value) -> str | None:
        """Serialize datetime values in ISO format."""
        if value is None:
            return None
        return value.isoformat()
