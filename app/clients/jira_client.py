from __future__ import annotations

from datetime import datetime
from typing import List

from app.clients.http_client import request_json
from app.models import Issue
from app.config import settings


def fetch_issues_by_jql(jql: str) -> List[Issue]:
    start_at = 0
    max_results = 50
    issues: List[Issue] = []
    headers = {"Authorization": f"Bearer {settings.jira_token}"}
    while True:
        url = f"{settings.jira_base_url}/rest/api/2/search"
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
        }
        data = request_json("GET", url, headers=headers, params=params)
        for item in data.get("issues", []):
            fields = item.get("fields", {})
            issues.append(
                Issue(
                    key=item["key"],
                    summary=fields.get("summary"),
                    description=fields.get("description"),
                    components=[c.get("name") for c in fields.get("components", [])],
                    fixversions=[v.get("name") for v in fields.get("fixVersions", [])],
                    updated=datetime.strptime(fields.get("updated"), "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None),
                )
            )
        start_at += max_results
        if start_at >= data.get("total", 0):
            break
    return issues
