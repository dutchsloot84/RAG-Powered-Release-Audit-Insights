from __future__ import annotations

import re
from typing import Dict, Iterable, List, Set

from app.models import Commit, Issue

JIRA_KEY_RE = re.compile(r"[A-Z][A-Z0-9]+-\d+")


def match_commits(issues: Iterable[Issue], commits: Iterable[Commit]) -> Dict:
    issue_keys: Set[str] = {i.key for i in issues}
    found_keys: Set[str] = set()
    commit_map: Dict[str, List[Commit]] = {}
    commits_list = list(commits)
    for commit in commits_list:
        keys = set(JIRA_KEY_RE.findall(commit.message or ""))
        for key in keys:
            commit_map.setdefault(key, []).append(commit)
        found_keys.update(keys & issue_keys)
    missing = sorted(issue_keys - found_keys)
    unlinked = [c for c in commits_list if not (set(JIRA_KEY_RE.findall(c.message or "")) & issue_keys)]
    coverage = (1 - len(missing) / len(issue_keys)) * 100 if issue_keys else 0
    return {
        "missing": missing,
        "unlinked": unlinked,
        "coverage": coverage,
        "links": commit_map,
    }
