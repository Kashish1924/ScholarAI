import re


def slugify(value: str) -> str:
    """Convert text into a URL-friendly slug."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    cleaned = normalized.strip("-")
    return cleaned or "scholarship"
