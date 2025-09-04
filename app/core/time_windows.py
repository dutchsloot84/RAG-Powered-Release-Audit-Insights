from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Tuple

from app.models import Issue


DEFAULT_BUFFER_DAYS = 7


def derive_window(issues: Iterable[Issue], buffer_days: int = DEFAULT_BUFFER_DAYS) -> Tuple[str, str]:
    """Return (start_iso, end_iso) covering all issue updates with buffer."""
    issues = list(issues)
    if not issues:
        raise ValueError("No issues provided")
    min_date = min(i.updated for i in issues) - timedelta(days=buffer_days)
    max_date = max(i.updated for i in issues) + timedelta(days=buffer_days)
    return min_date.isoformat(), max_date.isoformat()
