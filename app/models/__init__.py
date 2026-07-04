"""Database models package."""

from app.models.activity_log import ActivityLog
from app.models.admin import Admin
from app.models.bookmark import Bookmark
from app.models.contact_message import ContactMessage
from app.models.faq import FAQ
from app.models.news import News
from app.models.notification import Notification
from app.models.scholarship import Scholarship, ScholarshipCategory, ScholarshipState
from app.models.taxonomy import Category, State
from app.models.trending import TrendingScholarship

__all__ = [
    "ActivityLog",
    "Admin",
    "Bookmark",
    "Category",
    "ContactMessage",
    "FAQ",
    "News",
    "Notification",
    "Scholarship",
    "ScholarshipCategory",
    "ScholarshipState",
    "State",
    "TrendingScholarship",
]
