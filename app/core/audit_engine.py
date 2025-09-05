from __future__ import annotations

from typing import Dict, Iterable, Tuple

from app.cache.cache_manager import read_cache, write_cache
from app.clients import bitbucket_client, jira_client
from app.core import matching, time_windows


CACHE_PREFIX = "audit"


def run_audit(
    jql: str,
    repo_branches: Iterable[Tuple[str, str]],
    start: str | None = None,
    end: str | None = None,
    force_refresh: bool = False,
) -> Dict:
    """Run the end-to-end audit and cache the results."""

    cache_key = f"{CACHE_PREFIX}-{hash(jql)}"
    if not force_refresh:
        cached = read_cache(cache_key)
        if cached:
            return cached

    issues = jira_client.fetch_issues_by_jql(jql)
    if start is None or end is None:
        start, end = time_windows.derive_window(issues)
    commits = bitbucket_client.fetch_commits_threaded(repo_branches, start, end)
    match = matching.match_commits(issues, commits)
    result = {
        "issues": [i.dict() for i in issues],
        "commits": [c.dict() for c in commits],
        "matching": match,
        "window": {"start": start, "end": end},
    }
    write_cache(cache_key, result)
    return result
