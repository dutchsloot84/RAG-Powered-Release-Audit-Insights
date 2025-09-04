from __future__ import annotations

import argparse
from pathlib import Path

from app.core import audit_engine
from app.core import exporters


def parse_repo_pairs(text: str):
    pairs = []
    for part in text.split(","):
        if not part:
            continue
        repo, branch = part.split(":")
        pairs.append((repo.strip(), branch.strip()))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Run release audit")
    parser.add_argument("--jql", required=True, help="Jira JQL query")
    parser.add_argument(
        "--repos",
        required=True,
        help="Comma separated repo:branch pairs",
    )
    parser.add_argument("--update-cache", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--out", default="audit_results.json")
    args = parser.parse_args()

    pairs = parse_repo_pairs(args.repos)
    result = audit_engine.run_audit(args.jql, pairs, force_refresh=args.update_cache)
    path = Path(args.out)
    exporters.to_json(result, path)
    print(f"Results written to {path}")

    if not args.headless:
        print("Run 'streamlit run app/ui/ui_app.py' for the UI")


if __name__ == "__main__":
    main()
