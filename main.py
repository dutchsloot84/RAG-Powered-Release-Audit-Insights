from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path

from app.config import settings
from app.core import audit_engine, exporters


def _parse_csv(text: str) -> list[str]:
    return [p.strip() for p in text.split(",") if p.strip()]


def build_pairs(repos: list[str], branches: list[str]):
    pairs = []
    for repo, branch in product(repos, branches):
        repo_slug = (
            f"{settings.bitbucket.project_key}/{repo}" if "/" not in repo else repo
        )
        pairs.append((repo_slug, branch))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Run release audit")
    parser.add_argument(
        "--jql", default=settings.jira.jql_default, help="Jira JQL query"
    )
    parser.add_argument(
        "--repos",
        default=",".join(settings.bitbucket.repos),
        help="Comma separated repo slugs",
    )
    parser.add_argument(
        "--branches",
        default=",".join(settings.bitbucket.branch_defaults),
        help="Comma separated branch names",
    )
    parser.add_argument("--start-date", dest="start", help="Start date YYYY-MM-DD")
    parser.add_argument("--end-date", dest="end", help="End date YYYY-MM-DD")
    parser.add_argument("--update-cache", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--out", default="audit_results.json")
    args = parser.parse_args()

    repos = _parse_csv(args.repos) or settings.bitbucket.repos
    branches = _parse_csv(args.branches) or settings.bitbucket.branch_defaults
    pairs = build_pairs(repos, branches)
    result = audit_engine.run_audit(
        args.jql, pairs, start=args.start, end=args.end, force_refresh=args.update_cache
    )
    path = Path(args.out)
    exporters.to_json(result, path)
    print(f"Results written to {path}")

    if not args.headless:
        print("Run 'streamlit run app/ui/ui_app.py' for the UI")


if __name__ == "__main__":
    main()
