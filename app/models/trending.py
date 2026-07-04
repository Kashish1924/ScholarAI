from app.extensions import db
from app.models.base import TimestampMixin


class TrendingScholarship(TimestampMixin, db.Model):
    """Cached trending metrics to support fast homepage and analytics queries."""

    __tablename__ = "trending_scholarships"
    __table_args__ = (
        db.Index("ix_trending_score_rank", "computed_score", "last_computed_at"),
    )

    trending_id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(
        db.Integer,
        db.ForeignKey("scholarships.scholarship_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    bookmark_count_cache = db.Column(db.Integer, nullable=False, default=0)
    view_count_cache = db.Column(db.Integer, nullable=False, default=0)
    featured_weight = db.Column(db.Integer, nullable=False, default=0)
    freshness_weight = db.Column(db.Integer, nullable=False, default=0)
    computed_score = db.Column(db.Integer, nullable=False, default=0, index=True)
    last_computed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    scholarship = db.relationship("Scholarship", back_populates="trending_entry")

    def __repr__(self) -> str:
        return f"<TrendingScholarship {self.scholarship_id}>"
