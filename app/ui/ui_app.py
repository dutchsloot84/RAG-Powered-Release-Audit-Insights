from __future__ import annotations

import streamlit as st

from app.core.audit_engine import run_audit
from app.core.llm_client import (
    release_notes_summary,
    summarize_missing,
    suggest_regression_areas,
)
from app.core.rag_engine import build_corpus
from app.models import Commit, Issue


st.set_page_config(page_title="Release Audit", layout="wide")


def parse_repos(text: str):
    pairs = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        repo, branch = part.split(":")
        pairs.append((repo.strip(), branch.strip()))
    return pairs


def main():
    st.title("RAG-Based Release Audit")
    jql = st.sidebar.text_input("JQL Query")
    repo_text = st.sidebar.text_input("Bitbucket repos (proj/repo:branch)")
    refresh = st.sidebar.checkbox("Refresh Data")
    if not jql or not repo_text:
        st.info("Enter JQL and repositories to run the audit")
        return
    repo_pairs = parse_repos(repo_text)
    data = run_audit(jql, repo_pairs, force_refresh=refresh)
    issues = [Issue(**i) for i in data["issues"]]
    commits = [Commit(**c) for c in data["commits"]]
    match = data["matching"]
    corpus = build_corpus(issues, commits)

    tab_summary, tab_missing, tab_regression, tab_release, tab_rag = st.tabs(
        [
            "Audit Summary",
            "Missing Stories",
            "Regression Targets",
            "Release Notes",
            "RAG Search",
        ]
    )

    with tab_summary:
        st.metric("Coverage %", f"{match['coverage']:.1f}")
        st.write(f"Window: {data['window']['start']} → {data['window']['end']}")

    with tab_missing:
        st.write(match["missing"])
        if st.button("Summarize Missing Stories"):
            st.markdown(summarize_missing(match["missing"]))

    with tab_regression:
        if st.button("Generate Regression Summary"):
            st.markdown(suggest_regression_areas(commits))

    with tab_release:
        if st.button("Generate Release Notes"):
            st.markdown(release_notes_summary(issues))

    with tab_rag:
        q = st.text_input("Question")
        if st.button("Search") and q:
            results = corpus.search(q)
            for meta, text in results:
                st.write(meta, text)


if __name__ == "__main__":
    main()
