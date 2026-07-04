from app.extensions import db
from app.models.base import TimestampMixin


class Category(TimestampMixin, db.Model):
    """Master data for scholarship categories such as SC, ST, OBC, Merit."""

    __tablename__ = "categories"
    __table_args__ = (
        db.Index("ix_categories_name_active", "name", "is_active"),
    )

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    scholarship_links = db.relationship(
        "ScholarshipCategory",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class State(TimestampMixin, db.Model):
    """Master data for Indian states and union territories."""

    __tablename__ = "states"
    __table_args__ = (
        db.Index("ix_states_name_active", "name", "is_active"),
    )

    state_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=False, unique=True, index=True)
    is_union_territory = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    scholarship_links = db.relationship(
        "ScholarshipState",
        back_populates="state",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<State {self.code}>"
