from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel


class Issue(BaseModel):
    key: str
    summary: Optional[str] = ""
    description: Optional[str] = ""
    components: List[str] = []
    fixversions: List[str] = []
    updated: datetime


class Commit(BaseModel):
    sha: str
    author: Optional[str]
    date: datetime
    message: str
    repo: str
    branch: str
    files: Optional[List[str]] = None


class RapidToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    obtained_at: datetime

    @property
    def expires_at(self) -> datetime:
        return self.obtained_at + timedelta(seconds=self.expires_in)


class AuditResult(BaseModel):
    missing_stories: List[str]
    unlinked_commits: List[Commit]
    coverage: float
