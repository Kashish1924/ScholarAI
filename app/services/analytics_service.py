from datetime import date, timedelta

from sqlalchemy import func

from app.models import (
    Bookmark,
    Category,
    ContactMessage,
    Scholarship,
    ScholarshipCategory,
    ScholarshipState,
    State,
)


class AnalyticsService:
    """Analytics queries used by admin-facing APIs."""

    @staticmethod
    def get_dashboard_analytics() -> dict:
        """Return aggregated analytics payload."""
        today = date.today()
        upcoming_7 = today + timedelta(days=7)

        state_counts = (
            State.query.with_entities(State.name, ScholarshipState.scholarship_id)
            .join(ScholarshipState, ScholarshipState.state_id == State.state_id)
            .all()
        )
        category_counts = (
            Category.query.with_entities(Category.name, ScholarshipCategory.scholarship_id)
            .join(ScholarshipCategory, ScholarshipCategory.category_id == Category.category_id)
            .all()
        )

        return {
            "totals": {
                "total_scholarships": Scholarship.query.count(),
                "government_scholarships": Scholarship.query.filter_by(
                    scholarship_type="government"
                ).count(),
                "private_scholarships": Scholarship.query.filter_by(
                    scholarship_type="private"
                ).count(),
                "published_scholarships": Scholarship.query.filter_by(status="published").count(),
                "bookmark_count": Bookmark.query.count(),
                "contact_messages": ContactMessage.query.count(),
                "resolved_messages": ContactMessage.query.filter_by(is_resolved=True).count(),
            },
            "upcoming_deadlines": Scholarship.query.filter(
                Scholarship.status == "published",
                Scholarship.application_end_date >= today,
                Scholarship.application_end_date <= upcoming_7,
            ).count(),
            "most_viewed": [
                {
                    "scholarship_id": item.scholarship_id,
                    "scholarship_name": item.scholarship_name,
                    "view_count": item.view_count,
                }
                for item in Scholarship.query.order_by(Scholarship.view_count.desc()).limit(5).all()
            ],
            "most_bookmarked": [
                {
                    "scholarship_id": scholarship_id,
                    "scholarship_name": scholarship_name,
                    "bookmark_count": bookmark_count,
                }
                for scholarship_id, scholarship_name, bookmark_count in (
                    Scholarship.query.with_entities(
                        Scholarship.scholarship_id,
                        Scholarship.scholarship_name,
                        func.count(Bookmark.bookmark_id).label("bookmark_count"),
                    )
                    .outerjoin(Bookmark, Bookmark.scholarship_id == Scholarship.scholarship_id)
                    .group_by(Scholarship.scholarship_id, Scholarship.scholarship_name)
                    .order_by(func.count(Bookmark.bookmark_id).desc(), Scholarship.scholarship_name.asc())
                    .limit(5)
                    .all()
                )
            ],
            "trending": [
                {
                    "scholarship_id": item.scholarship_id,
                    "scholarship_name": item.scholarship_name,
                    "trending_score": item.trending_score,
                }
                for item in Scholarship.query.order_by(Scholarship.trending_score.desc()).limit(5).all()
            ],
            "state_wise_count": AnalyticsService._count_named_records(state_counts),
            "category_wise_count": AnalyticsService._count_named_records(category_counts),
            "charts": {
                "type_distribution": {
                    "labels": ["Government", "Private"],
                    "values": [
                        Scholarship.query.filter_by(scholarship_type="government").count(),
                        Scholarship.query.filter_by(scholarship_type="private").count(),
                    ],
                },
                "publication_distribution": {
                    "labels": ["Published", "Draft", "Archived"],
                    "values": [
                        Scholarship.query.filter_by(status="published").count(),
                        Scholarship.query.filter_by(status="draft").count(),
                        Scholarship.query.filter_by(status="archived").count(),
                    ],
                },
            },
        }

    @staticmethod
    def _count_named_records(rows: list[tuple[str, int]]) -> list[dict]:
        """Fold joined rows into named aggregate counts."""
        counts = {}
        for name, _ in rows:
            counts[name] = counts.get(name, 0) + 1
        return [
            {"name": name, "count": count}
            for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]
