"""Placeholder for future GitHub client implementation."""

from __future__ import annotations

from typing import List

from app.models import Commit


def fetch_commits(*args, **kwargs) -> List[Commit]:
    raise NotImplementedError("GitHub support not implemented yet")
