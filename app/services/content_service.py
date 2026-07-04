from datetime import datetime, timezone

from app.models import FAQ, News, Notification


class ContentService:
    """Read-focused services for public content modules."""

    @staticmethod
    def list_news(page: int = 1, per_page: int = 10, published_only: bool = True) -> dict:
        """Return paginated news records."""
        page = max(page, 1)
        per_page = min(max(per_page, 1), 50)

        query = News.query
        if published_only:
            query = query.filter_by(is_published=True)

        pagination = query.order_by(
            News.priority.desc(),
            News.published_at.desc(),
            News.created_at.desc(),
        ).paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": [ContentService.serialize_news(item) for item in pagination.items],
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
    def list_faqs(published_only: bool = True) -> list[dict]:
        """Return FAQ records in display order."""
        query = FAQ.query
        if published_only:
            query = query.filter_by(is_published=True)

        return [
            ContentService.serialize_faq(item)
            for item in query.order_by(FAQ.display_order.asc(), FAQ.created_at.desc()).all()
        ]

    @staticmethod
    def list_active_notifications(audience_type: str = "all") -> list[dict]:
        """Return active notifications available for the requested audience."""
        now = datetime.now(timezone.utc)
        query = Notification.query.filter(Notification.is_active.is_(True))
        query = query.filter(Notification.audience_type.in_(["all", audience_type]))
        query = query.filter(
            (Notification.starts_at.is_(None) | (Notification.starts_at <= now))
        )
        query = query.filter(
            (Notification.ends_at.is_(None) | (Notification.ends_at >= now))
        )

        return [
            ContentService.serialize_notification(item)
            for item in query.order_by(Notification.created_at.desc()).all()
        ]

    @staticmethod
    def serialize_news(news: News) -> dict:
        """Serialize news record."""
        return {
            "news_id": news.news_id,
            "title": news.title,
            "slug": news.slug,
            "summary": news.summary,
            "content": news.content,
            "source_url": news.source_url,
            "image_url": news.image_url,
            "priority": news.priority,
            "is_published": news.is_published,
            "published_at": news.published_at.isoformat() if news.published_at else None,
            "related_scholarship_id": news.related_scholarship_id,
            "created_at": news.created_at.isoformat(),
            "updated_at": news.updated_at.isoformat(),
        }

    @staticmethod
    def serialize_faq(faq: FAQ) -> dict:
        """Serialize FAQ record."""
        return {
            "faq_id": faq.faq_id,
            "question": faq.question,
            "answer": faq.answer,
            "display_order": faq.display_order,
            "is_published": faq.is_published,
            "created_at": faq.created_at.isoformat(),
            "updated_at": faq.updated_at.isoformat(),
        }

    @staticmethod
    def serialize_notification(notification: Notification) -> dict:
        """Serialize notification record."""
        return {
            "notification_id": notification.notification_id,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "audience_type": notification.audience_type,
            "is_active": notification.is_active,
            "starts_at": notification.starts_at.isoformat() if notification.starts_at else None,
            "ends_at": notification.ends_at.isoformat() if notification.ends_at else None,
            "related_scholarship_id": notification.related_scholarship_id,
            "created_at": notification.created_at.isoformat(),
            "updated_at": notification.updated_at.isoformat(),
        }
