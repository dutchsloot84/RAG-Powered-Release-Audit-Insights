from __future__ import annotations

import streamlit as st

from app.config import settings
from app.core.audit_engine import run_audit
from app.core.llm_client import (
    release_notes_summary,
    summarize_missing,
    suggest_regression_areas,
)
from app.core.rag_engine import build_corpus
from app.models import Commit, Issue


st.set_page_config(page_title="Release Audit", layout="wide")


def main():
    st.title("RAG-Based Release Audit")
    jql = st.sidebar.text_input("JQL Query", value=settings.jira.jql_default)
    repos = st.sidebar.multiselect(
        "Repositories",
        options=settings.bitbucket.repos,
        default=settings.bitbucket.repos,
    )
    branches = st.sidebar.multiselect(
        "Branches",
        options=settings.bitbucket.branch_defaults,
        default=settings.bitbucket.branch_defaults,
    )
    start = st.sidebar.date_input("Start date", value=None)
    end = st.sidebar.date_input("End date", value=None)
    refresh = st.sidebar.checkbox("Refresh Data")
    run = st.sidebar.button("Run audit")
    if not run or not jql:
        st.info("Enter parameters and run the audit")
        return
    repo_pairs = [
        (f"{settings.bitbucket.project_key}/{r}", b) for r in repos for b in branches
    ]
    start_iso = start.isoformat() if hasattr(start, "isoformat") else None
    end_iso = end.isoformat() if hasattr(end, "isoformat") else None
    data = run_audit(jql, repo_pairs, start_iso, end_iso, force_refresh=refresh)
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
