from app.extensions import db
from app.models.base import TimestampMixin


class Scholarship(TimestampMixin, db.Model):
    """Canonical scholarship record used across student and admin modules."""

    __tablename__ = "scholarships"
    __table_args__ = (
        db.Index("ix_scholarships_name_status", "scholarship_name", "status"),
        db.Index("ix_scholarships_type_amount", "scholarship_type", "scholarship_amount"),
        db.Index(
            "ix_scholarships_income_cgpa_deadline",
            "maximum_family_income",
            "minimum_cgpa",
            "application_end_date",
        ),
    )

    scholarship_id = db.Column(db.Integer, primary_key=True)
    scholarship_name = db.Column(db.String(255), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    provider_name = db.Column(db.String(255), nullable=False, index=True)
    scholarship_type = db.Column(db.String(50), nullable=False, index=True)
    scholarship_amount = db.Column(db.Numeric(12, 2), nullable=True)
    eligibility_description = db.Column(db.Text, nullable=False)
    minimum_cgpa = db.Column(db.Numeric(4, 2), nullable=True)
    maximum_family_income = db.Column(db.Numeric(12, 2), nullable=True)
    gender = db.Column(db.String(30), nullable=False, default="all", index=True)
    degree = db.Column(db.String(100), nullable=False, index=True)
    branch = db.Column(db.String(100), nullable=False, index=True)
    academic_year = db.Column(db.String(30), nullable=False, index=True)
    minority_eligibility = db.Column(db.Boolean, nullable=False, default=False)
    disability_eligibility = db.Column(db.Boolean, nullable=False, default=False)
    hosteller_eligibility = db.Column(db.Boolean, nullable=False, default=False)
    day_scholar_eligibility = db.Column(db.Boolean, nullable=False, default=False)
    required_documents = db.Column(db.Text, nullable=True)
    application_link = db.Column(db.String(500), nullable=False)
    official_website = db.Column(db.String(500), nullable=False)
    application_start_date = db.Column(db.Date, nullable=True)
    application_end_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="draft", index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    trending_score = db.Column(db.Integer, nullable=False, default=0, index=True)
    description = db.Column(db.Text, nullable=False)
    benefits = db.Column(db.Text, nullable=True)
    selection_process = db.Column(db.Text, nullable=True)
    is_renewable = db.Column(db.Boolean, nullable=False, default=False)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    last_verified_at = db.Column(db.DateTime(timezone=True), nullable=True)

    bookmarks = db.relationship(
        "Bookmark",
        back_populates="scholarship",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    categories = db.relationship(
        "ScholarshipCategory",
        back_populates="scholarship",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    states = db.relationship(
        "ScholarshipState",
        back_populates="scholarship",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    related_news = db.relationship("News", back_populates="related_scholarship", lazy="dynamic")
    notifications = db.relationship(
        "Notification",
        back_populates="related_scholarship",
        lazy="dynamic",
    )
    trending_entry = db.relationship(
        "TrendingScholarship",
        back_populates="scholarship",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Scholarship {self.scholarship_name}>"


class ScholarshipCategory(TimestampMixin, db.Model):
    """Join table for many-to-many scholarship and category eligibility mapping."""

    __tablename__ = "scholarship_categories"
    __table_args__ = (
        db.UniqueConstraint(
            "scholarship_id",
            "category_id",
            name="uq_scholarship_category_pair",
        ),
        db.Index("ix_scholarship_categories_lookup", "scholarship_id", "category_id"),
    )

    scholarship_category_id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(
        db.Integer,
        db.ForeignKey("scholarships.scholarship_id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id", ondelete="CASCADE"),
        nullable=False,
    )

    scholarship = db.relationship("Scholarship", back_populates="categories")
    category = db.relationship("Category", back_populates="scholarship_links")


class ScholarshipState(TimestampMixin, db.Model):
    """Join table for many-to-many scholarship and state eligibility mapping."""

    __tablename__ = "scholarship_states"
    __table_args__ = (
        db.UniqueConstraint(
            "scholarship_id",
            "state_id",
            name="uq_scholarship_state_pair",
        ),
        db.Index("ix_scholarship_states_lookup", "scholarship_id", "state_id"),
    )

    scholarship_state_id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(
        db.Integer,
        db.ForeignKey("scholarships.scholarship_id", ondelete="CASCADE"),
        nullable=False,
    )
    state_id = db.Column(
        db.Integer,
        db.ForeignKey("states.state_id", ondelete="CASCADE"),
        nullable=False,
    )

    scholarship = db.relationship("Scholarship", back_populates="states")
    state = db.relationship("State", back_populates="scholarship_links")
