from __future__ import annotations

from typing import Iterable, List

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

from app.config import settings
from app.models import Commit, Issue


def _get_client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError("openai package not installed")
    return OpenAI(api_key=settings.openai_api_key)


def _chat(prompt: str) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def summarize_missing(missing_keys: Iterable[str]) -> str:
    if not missing_keys:
        return "All stories are linked to commits."
    prompt = (
        "You are a release auditor. Summarize the following Jira keys that are missing commits: "
        + ", ".join(missing_keys)
    )
    return _chat(prompt)


def suggest_regression_areas(commits: Iterable[Commit]) -> str:
    msgs = [c.message for c in commits]
    prompt = "Suggest regression test areas based on these commit messages:\n" + "\n".join(msgs)
    return _chat(prompt)


def release_notes_summary(issues: Iterable[Issue]) -> str:
    summaries = [f"- {i.key}: {i.summary}" for i in issues]
    prompt = "Generate concise release notes from the following issues:\n" + "\n".join(summaries)
    return _chat(prompt)
