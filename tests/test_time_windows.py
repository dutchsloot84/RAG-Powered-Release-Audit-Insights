from datetime import datetime

from app.core import time_windows
from app.models import Issue


def test_window_derivation():
    base = datetime(2024, 1, 15)
    issues = [
        Issue(key="A-1", summary="", description="", components=[], fixversions=[], updated=base),
        Issue(key="A-2", summary="", description="", components=[], fixversions=[], updated=base.replace(day=20)),
    ]
    start, end = time_windows.derive_window(issues, buffer_days=1)
    assert start.startswith("2024-01-14")
    assert end.startswith("2024-01-21")
