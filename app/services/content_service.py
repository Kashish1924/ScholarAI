from datetime import datetime, timezone

from app.extensions import db
from app.models import ContactMessage, FAQ, News, Notification, Scholarship
from app.utils.slug import slugify
from app.utils.validation import ValidationError


class ContentService:
    """Read-focused services for public content modules."""

    @staticmethod
    def list_news_records(limit: int = 100) -> list[News]:
        """Return admin-facing news records."""
        return News.query.order_by(News.created_at.desc()).limit(max(limit, 1)).all()

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
    def get_news_by_id(news_id: int) -> News | None:
        """Return a news record by id."""
        return News.query.filter_by(news_id=news_id).first()

    @staticmethod
    def create_news(payload: dict, admin_id: int | None = None) -> News:
        """Create a news record."""
        clean = ContentService._validate_news_payload(payload)
        news = News(
            title=clean["title"],
            slug=ContentService._generate_unique_news_slug(clean["title"]),
            summary=clean["summary"],
            content=clean["content"],
            source_url=clean.get("source_url"),
            image_url=clean.get("image_url"),
            priority=clean["priority"],
            is_published=clean["is_published"],
            published_at=datetime.now(timezone.utc) if clean["is_published"] else None,
            created_by_admin_id=admin_id,
            related_scholarship_id=clean.get("related_scholarship_id"),
        )
        db.session.add(news)
        db.session.commit()
        return news

    @staticmethod
    def update_news(news_id: int, payload: dict) -> News | None:
        """Update a news record."""
        news = ContentService.get_news_by_id(news_id)
        if news is None:
            return None
        clean = ContentService._validate_news_payload(payload)
        news.title = clean["title"]
        news.slug = ContentService._generate_unique_news_slug(clean["title"], news.news_id)
        news.summary = clean["summary"]
        news.content = clean["content"]
        news.source_url = clean.get("source_url")
        news.image_url = clean.get("image_url")
        news.priority = clean["priority"]
        news.is_published = clean["is_published"]
        news.published_at = datetime.now(timezone.utc) if clean["is_published"] else None
        news.related_scholarship_id = clean.get("related_scholarship_id")
        db.session.commit()
        return news

    @staticmethod
    def delete_news(news_id: int) -> bool:
        """Delete a news record."""
        news = ContentService.get_news_by_id(news_id)
        if news is None:
            return False
        db.session.delete(news)
        db.session.commit()
        return True

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
    def list_faq_records() -> list[FAQ]:
        """Return admin-facing FAQ records."""
        return FAQ.query.order_by(FAQ.display_order.asc(), FAQ.created_at.desc()).all()

    @staticmethod
    def get_faq_by_id(faq_id: int) -> FAQ | None:
        """Return FAQ by id."""
        return FAQ.query.filter_by(faq_id=faq_id).first()

    @staticmethod
    def create_faq(payload: dict, admin_id: int | None = None) -> FAQ:
        """Create an FAQ record."""
        clean = ContentService._validate_faq_payload(payload)
        faq = FAQ(
            question=clean["question"],
            answer=clean["answer"],
            display_order=clean["display_order"],
            is_published=clean["is_published"],
            created_by_admin_id=admin_id,
        )
        db.session.add(faq)
        db.session.commit()
        return faq

    @staticmethod
    def update_faq(faq_id: int, payload: dict) -> FAQ | None:
        """Update an FAQ record."""
        faq = ContentService.get_faq_by_id(faq_id)
        if faq is None:
            return None
        clean = ContentService._validate_faq_payload(payload)
        faq.question = clean["question"]
        faq.answer = clean["answer"]
        faq.display_order = clean["display_order"]
        faq.is_published = clean["is_published"]
        db.session.commit()
        return faq

    @staticmethod
    def delete_faq(faq_id: int) -> bool:
        """Delete an FAQ record."""
        faq = ContentService.get_faq_by_id(faq_id)
        if faq is None:
            return False
        db.session.delete(faq)
        db.session.commit()
        return True

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
    def list_notification_records() -> list[Notification]:
        """Return admin-facing notification records."""
        return Notification.query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_notification_by_id(notification_id: int) -> Notification | None:
        """Return notification by id."""
        return Notification.query.filter_by(notification_id=notification_id).first()

    @staticmethod
    def create_notification(payload: dict, admin_id: int | None = None) -> Notification:
        """Create a notification record."""
        clean = ContentService._validate_notification_payload(payload)
        notification = Notification(
            title=clean["title"],
            message=clean["message"],
            notification_type=clean["notification_type"],
            audience_type=clean["audience_type"],
            is_active=clean["is_active"],
            starts_at=clean.get("starts_at"),
            ends_at=clean.get("ends_at"),
            created_by_admin_id=admin_id,
            related_scholarship_id=clean.get("related_scholarship_id"),
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def update_notification(notification_id: int, payload: dict) -> Notification | None:
        """Update a notification record."""
        notification = ContentService.get_notification_by_id(notification_id)
        if notification is None:
            return None
        clean = ContentService._validate_notification_payload(payload)
        notification.title = clean["title"]
        notification.message = clean["message"]
        notification.notification_type = clean["notification_type"]
        notification.audience_type = clean["audience_type"]
        notification.is_active = clean["is_active"]
        notification.starts_at = clean.get("starts_at")
        notification.ends_at = clean.get("ends_at")
        notification.related_scholarship_id = clean.get("related_scholarship_id")
        db.session.commit()
        return notification

    @staticmethod
    def delete_notification(notification_id: int) -> bool:
        """Delete a notification record."""
        notification = ContentService.get_notification_by_id(notification_id)
        if notification is None:
            return False
        db.session.delete(notification)
        db.session.commit()
        return True

    @staticmethod
    def create_contact_message(payload: dict) -> ContactMessage:
        """Create a public contact message."""
        clean = ContentService._validate_contact_payload(payload)
        message = ContactMessage(
            full_name=clean["full_name"],
            email=clean["email"],
            subject=clean["subject"],
            message=clean["message"],
        )
        db.session.add(message)
        db.session.commit()
        return message

    @staticmethod
    def list_contact_messages(limit: int = 100, resolved: bool | None = None) -> list[ContactMessage]:
        """Return admin-facing contact messages."""
        query = ContactMessage.query
        if resolved is not None:
            query = query.filter_by(is_resolved=resolved)
        return query.order_by(
            ContactMessage.is_resolved.asc(),
            ContactMessage.created_at.desc(),
        ).limit(max(limit, 1)).all()

    @staticmethod
    def get_contact_message_by_id(message_id: int) -> ContactMessage | None:
        """Return a contact message by id."""
        return ContactMessage.query.filter_by(message_id=message_id).first()

    @staticmethod
    def resolve_contact_message(message_id: int, admin_id: int | None = None) -> ContactMessage | None:
        """Mark a contact message as resolved."""
        message = ContentService.get_contact_message_by_id(message_id)
        if message is None:
            return None

        if not message.is_resolved:
            message.is_resolved = True
            message.resolved_at = datetime.now(timezone.utc)
            message.resolved_by_admin_id = admin_id
            db.session.commit()
        return message

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

    @staticmethod
    def serialize_contact_message(message: ContactMessage) -> dict:
        """Serialize contact message record."""
        return {
            "message_id": message.message_id,
            "full_name": message.full_name,
            "email": message.email,
            "subject": message.subject,
            "message": message.message,
            "is_resolved": message.is_resolved,
            "resolved_at": message.resolved_at.isoformat() if message.resolved_at else None,
            "resolved_by_admin_id": message.resolved_by_admin_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
        }

    @staticmethod
    def _validate_news_payload(payload: dict) -> dict:
        """Validate create or update payload for news."""
        errors = {}
        title = (payload.get("title") or "").strip()
        summary = (payload.get("summary") or "").strip()
        content = (payload.get("content") or "").strip()
        if not title:
            errors.setdefault("title", []).append("Title is required.")
        if not summary:
            errors.setdefault("summary", []).append("Summary is required.")
        if not content:
            errors.setdefault("content", []).append("Content is required.")

        related_scholarship_id = payload.get("related_scholarship_id")
        if related_scholarship_id in ("", None):
            related_scholarship_id = None
        elif Scholarship.query.filter_by(scholarship_id=related_scholarship_id).first() is None:
            errors.setdefault("related_scholarship_id", []).append("Related scholarship does not exist.")

        if errors:
            raise ValidationError(errors)

        return {
            "title": title,
            "summary": summary,
            "content": content,
            "source_url": (payload.get("source_url") or "").strip() or None,
            "image_url": (payload.get("image_url") or "").strip() or None,
            "priority": int(payload.get("priority") or 0),
            "is_published": bool(payload.get("is_published")),
            "related_scholarship_id": related_scholarship_id,
        }

    @staticmethod
    def _validate_faq_payload(payload: dict) -> dict:
        """Validate FAQ payload."""
        errors = {}
        question = (payload.get("question") or "").strip()
        answer = (payload.get("answer") or "").strip()
        if not question:
            errors.setdefault("question", []).append("Question is required.")
        if not answer:
            errors.setdefault("answer", []).append("Answer is required.")
        if errors:
            raise ValidationError(errors)
        return {
            "question": question,
            "answer": answer,
            "display_order": int(payload.get("display_order") or 0),
            "is_published": bool(payload.get("is_published")),
        }

    @staticmethod
    def _validate_notification_payload(payload: dict) -> dict:
        """Validate notification payload."""
        errors = {}
        title = (payload.get("title") or "").strip()
        message = (payload.get("message") or "").strip()
        if not title:
            errors.setdefault("title", []).append("Title is required.")
        if not message:
            errors.setdefault("message", []).append("Message is required.")

        related_scholarship_id = payload.get("related_scholarship_id")
        if related_scholarship_id in ("", None):
            related_scholarship_id = None
        elif Scholarship.query.filter_by(scholarship_id=related_scholarship_id).first() is None:
            errors.setdefault("related_scholarship_id", []).append("Related scholarship does not exist.")

        starts_at = ContentService._parse_datetime(payload.get("starts_at"), "starts_at", errors)
        ends_at = ContentService._parse_datetime(payload.get("ends_at"), "ends_at", errors)
        if starts_at and ends_at and starts_at > ends_at:
            errors.setdefault("starts_at", []).append("Start time must be before end time.")

        if errors:
            raise ValidationError(errors)

        return {
            "title": title,
            "message": message,
            "notification_type": (payload.get("notification_type") or "general").strip().lower(),
            "audience_type": (payload.get("audience_type") or "all").strip().lower(),
            "is_active": bool(payload.get("is_active")),
            "starts_at": starts_at,
            "ends_at": ends_at,
            "related_scholarship_id": related_scholarship_id,
        }

    @staticmethod
    def _generate_unique_news_slug(title: str, news_id: int | None = None) -> str:
        """Generate a unique slug for news records."""
        base_slug = slugify(title)
        candidate = base_slug
        counter = 2
        while True:
            existing = News.query.filter_by(slug=candidate).first()
            if existing is None or existing.news_id == news_id:
                return candidate
            candidate = f"{base_slug}-{counter}"
            counter += 1

    @staticmethod
    def _parse_datetime(value, field_name: str, errors: dict):
        """Parse HTML datetime-local values."""
        if value in (None, ""):
            return None
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            errors.setdefault(field_name, []).append("Must use a valid datetime format.")
            return None

    @staticmethod
    def _validate_contact_payload(payload: dict) -> dict:
        """Validate public contact form input."""
        errors = {}
        full_name = (payload.get("full_name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        subject = (payload.get("subject") or "").strip()
        message = (payload.get("message") or "").strip()

        if not full_name:
            errors.setdefault("full_name", []).append("Full name is required.")
        if not email or "@" not in email:
            errors.setdefault("email", []).append("A valid email address is required.")
        if not subject:
            errors.setdefault("subject", []).append("Subject is required.")
        if not message:
            errors.setdefault("message", []).append("Message is required.")

        if full_name and len(full_name) > 120:
            errors.setdefault("full_name", []).append("Full name must be 120 characters or fewer.")
        if email and len(email) > 255:
            errors.setdefault("email", []).append("Email must be 255 characters or fewer.")
        if subject and len(subject) > 255:
            errors.setdefault("subject", []).append("Subject must be 255 characters or fewer.")
        if message and len(message) > 3000:
            errors.setdefault("message", []).append("Message must be 3000 characters or fewer.")

        if errors:
            raise ValidationError(errors)

        return {
            "full_name": full_name,
            "email": email,
            "subject": subject,
            "message": message,
        }
