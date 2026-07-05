from flask import Blueprint, request, session

from app.extensions import db
from app.models import Category, State
from app.utils.api import error_response, success_response


seed_bp = Blueprint("seed", __name__)


def _require_admin_api_access():
    """Require an authenticated admin session for taxonomy mutations."""
    if not session.get("admin_id"):
        return error_response(
            "Admin authentication is required for this action.",
            status_code=401,
        )
    return None


@seed_bp.get("/taxonomy/categories")
def list_categories():
    """Return category taxonomy records."""
    categories = Category.query.order_by(Category.name.asc()).all()
    return success_response(
        "Categories fetched successfully.",
        data=[
            {
                "category_id": category.category_id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "is_active": category.is_active,
            }
            for category in categories
        ],
    )


@seed_bp.get("/taxonomy/states")
def list_states():
    """Return state taxonomy records."""
    states = State.query.order_by(State.name.asc()).all()
    return success_response(
        "States fetched successfully.",
        data=[
            {
                "state_id": state.state_id,
                "name": state.name,
                "code": state.code,
                "is_union_territory": state.is_union_territory,
                "is_active": state.is_active,
            }
            for state in states
        ],
    )


@seed_bp.post("/taxonomy/categories")
def create_category():
    """Create a category lookup record."""
    auth_error = _require_admin_api_access()
    if auth_error:
        return auth_error

    payload = request.get_json(silent=True)
    if payload is None:
        return error_response("Request body must be valid JSON.", status_code=400)

    name = (payload.get("name") or "").strip()
    slug = (payload.get("slug") or "").strip().lower()
    description = (payload.get("description") or "").strip() or None

    if not name or not slug:
        return error_response(
            "Category validation failed.",
            errors={"name": ["Name is required."], "slug": ["Slug is required."]},
            status_code=422,
        )

    if Category.query.filter((Category.name == name) | (Category.slug == slug)).first():
        return error_response(
            "Category already exists.",
            status_code=409,
        )

    category = Category(name=name, slug=slug, description=description)
    db.session.add(category)
    db.session.commit()

    return success_response(
        "Category created successfully.",
        data={
            "category_id": category.category_id,
            "name": category.name,
            "slug": category.slug,
        },
        status_code=201,
    )


@seed_bp.post("/taxonomy/states")
def create_state():
    """Create a state lookup record."""
    auth_error = _require_admin_api_access()
    if auth_error:
        return auth_error

    payload = request.get_json(silent=True)
    if payload is None:
        return error_response("Request body must be valid JSON.", status_code=400)

    name = (payload.get("name") or "").strip()
    code = (payload.get("code") or "").strip().upper()
    raw_flag = payload.get("is_union_territory", False)
    is_union_territory = False
    if isinstance(raw_flag, bool):
        is_union_territory = raw_flag
    elif isinstance(raw_flag, str):
        normalized = raw_flag.strip().lower()
        if normalized in {"true", "1", "yes"}:
            is_union_territory = True
        elif normalized in {"false", "0", "no"}:
            is_union_territory = False
        else:
            return error_response(
                "State validation failed.",
                errors={
                    "is_union_territory": ["Must be a boolean value."]
                },
                status_code=422,
            )
    else:
        return error_response(
            "State validation failed.",
            errors={"is_union_territory": ["Must be a boolean value."]},
            status_code=422,
        )

    if not name or not code:
        return error_response(
            "State validation failed.",
            errors={"name": ["Name is required."], "code": ["Code is required."]},
            status_code=422,
        )

    if State.query.filter((State.name == name) | (State.code == code)).first():
        return error_response(
            "State already exists.",
            status_code=409,
        )

    state = State(name=name, code=code, is_union_territory=is_union_territory)
    db.session.add(state)
    db.session.commit()

    return success_response(
        "State created successfully.",
        data={
            "state_id": state.state_id,
            "name": state.name,
            "code": state.code,
        },
        status_code=201,
    )
