from app.models import FAQ, News, Notification


def build_news_payload_from_form(form) -> dict:
    """Convert news form input to service payload."""
    return {
        "title": form.title.data,
        "summary": form.summary.data,
        "content": form.content.data,
        "source_url": form.source_url.data,
        "image_url": form.image_url.data,
        "priority": form.priority.data or 0,
        "is_published": form.is_published.data,
        "related_scholarship_id": form.related_scholarship_id.data,
    }


def build_faq_payload_from_form(form) -> dict:
    """Convert FAQ form input to service payload."""
    return {
        "question": form.question.data,
        "answer": form.answer.data,
        "display_order": form.display_order.data or 0,
        "is_published": form.is_published.data,
    }


def build_notification_payload_from_form(form) -> dict:
    """Convert notification form input to service payload."""
    return {
        "title": form.title.data,
        "message": form.message.data,
        "notification_type": form.notification_type.data,
        "audience_type": form.audience_type.data,
        "is_active": form.is_active.data,
        "starts_at": form.starts_at.data,
        "ends_at": form.ends_at.data,
        "related_scholarship_id": form.related_scholarship_id.data,
    }


def news_to_form_payload(news: News) -> dict:
    """Convert a news record to form-friendly values."""
    return {
        "title": news.title,
        "summary": news.summary,
        "content": news.content,
        "source_url": news.source_url or "",
        "image_url": news.image_url or "",
        "priority": news.priority,
        "is_published": news.is_published,
        "related_scholarship_id": news.related_scholarship_id or "",
    }


def faq_to_form_payload(faq: FAQ) -> dict:
    """Convert an FAQ record to form-friendly values."""
    return {
        "question": faq.question,
        "answer": faq.answer,
        "display_order": faq.display_order,
        "is_published": faq.is_published,
    }


def notification_to_form_payload(notification: Notification) -> dict:
    """Convert a notification record to form-friendly values."""
    return {
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "audience_type": notification.audience_type,
        "is_active": notification.is_active,
        "starts_at": notification.starts_at.isoformat(timespec="minutes") if notification.starts_at else "",
        "ends_at": notification.ends_at.isoformat(timespec="minutes") if notification.ends_at else "",
        "related_scholarship_id": notification.related_scholarship_id or "",
    }
