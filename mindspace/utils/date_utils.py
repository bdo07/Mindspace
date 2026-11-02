"""Date and time formatting helpers."""

from datetime import date, datetime, timedelta
from typing import Optional, Tuple


def parse_iso(iso_str: Optional[str]) -> Optional[datetime]:
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except Exception:
        return None


def format_relative_date(iso_str: Optional[str]) -> str:
    """Formats an ISO timestamp into a clean relative date string."""
    dt = parse_iso(iso_str)
    if not dt:
        return ""

    today = date.today()
    item_date = dt.date()

    if item_date == today:
        return f"Today, {dt.strftime('%H:%M')}"
    elif item_date == today - timedelta(days=1):
        return f"Yesterday, {dt.strftime('%H:%M')}"
    elif item_date.year == today.year:
        return dt.strftime("%b %d")
    else:
        return dt.strftime("%b %d, %Y")


def format_due_date(due_str: Optional[str]) -> Tuple[str, str]:
    """
    Returns (display_text, status_class).
    status_class is one of: 'overdue', 'today', 'tomorrow', 'upcoming', 'none'.
    """
    if not due_str:
        return "", "none"

    try:
        if "T" in due_str:
            due_d = datetime.fromisoformat(due_str).date()
        else:
            due_d = date.fromisoformat(due_str)
    except Exception:
        return due_str, "upcoming"

    today = date.today()
    diff = (due_d - today).days

    if diff < 0:
        days = abs(diff)
        text = f"Overdue ({days}d)" if days > 1 else "Overdue (1d)"
        return text, "overdue"
    elif diff == 0:
        return "Due Today", "today"
    elif diff == 1:
        return "Due Tomorrow", "tomorrow"
    elif diff <= 7:
        return f"Due in {diff}d", "upcoming"
    else:
        return due_d.strftime("%b %d"), "upcoming"

