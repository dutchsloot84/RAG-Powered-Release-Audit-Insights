from __future__ import annotations

from typing import Iterable, List, Tuple

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None

from app.config import settings
from app.models import Commit, Issue


class SimpleCorpus:
    def __init__(self, texts: List[str], metadata: List[Tuple[str, str]]):
        self.texts = texts
        self.metadata = metadata

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, str, str]]:
        results = []
        q = query.lower()
        for text, meta in zip(self.texts, self.metadata):
            score = text.lower().count(q)
            if score:
                results.append((score, text, meta))
        results.sort(reverse=True)
        return [(m, t) for s, t, m in results[:top_k]]


def build_corpus(issues: Iterable[Issue], commits: Iterable[Commit]) -> SimpleCorpus:
    texts: List[str] = []
    metadata: List[Tuple[str, str]] = []
    for issue in issues:
        text = f"{issue.key} {issue.summary} {issue.description} {' '.join(issue.components)}"
        texts.append(text)
        metadata.append(("issue", issue.key))
    for commit in commits:
        text = f"{commit.message}"
        texts.append(text)
        metadata.append(("commit", commit.sha))
    return SimpleCorpus(texts, metadata)
