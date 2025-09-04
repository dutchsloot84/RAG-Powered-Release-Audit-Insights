from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from app.clients.http_client import request_json
from app.config import settings
from app.models import Commit


def _fetch_commits_page(repo: str, branch: str, start: int, since: str, until: str) -> Dict:
    project, slug = repo.split("/")
    url = f"{settings.bitbucket_base_url}/rest/api/1.0/projects/{project}/repos/{slug}/commits"
    params = {
        "limit": 100,
        "start": start,
        "until": branch,
        "since": since,
        "untilDate": until,
    }
    headers = {"Authorization": f"Bearer {settings.bitbucket_token}"}
    return request_json("GET", url, headers=headers, params=params)


def fetch_commits(repo: str, branch: str, start_date: str, end_date: str) -> List[Commit]:
    commits: List[Commit] = []
    start = 0
    while True:
        data = _fetch_commits_page(repo, branch, start, start_date, end_date)
        for item in data.get("values", []):
            ts = int(item.get("authorTimestamp")) / 1000
            commits.append(
                Commit(
                    sha=item.get("id"),
                    author=(item.get("author", {}) or {}).get("name"),
                    date=datetime.utcfromtimestamp(ts),
                    message=item.get("message"),
                    repo=repo,
                    branch=branch,
                )
            )
        if data.get("isLastPage", True):
            break
        start = data.get("nextPageStart", 0)
    return commits


def fetch_commits_threaded(pairs: Iterable[Tuple[str, str]], start_date: str, end_date: str) -> List[Commit]:
    results: List[Commit] = []
    with ThreadPoolExecutor(max_workers=settings.threads) as executor:
        futures = [
            executor.submit(fetch_commits, repo, branch, start_date, end_date)
            for repo, branch in pairs
        ]
        for fut in futures:
            results.extend(fut.result())
    return results
