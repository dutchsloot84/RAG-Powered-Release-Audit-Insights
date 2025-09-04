from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from app.cache.cache_manager import read_cache, write_cache
from app.clients import jira_client, bitbucket_client
from app.core import matching, time_windows
from app.models import Commit, Issue


CACHE_PREFIX = "audit"


def run_audit(jql: str, repo_branches: Iterable[Tuple[str, str]], force_refresh: bool = False) -> Dict:
    cache_key = f"{CACHE_PREFIX}-{hash(jql)}"
    if not force_refresh:
        cached = read_cache(cache_key)
        if cached:
            return cached

    issues = jira_client.fetch_issues_by_jql(jql)
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
