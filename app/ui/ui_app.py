from __future__ import annotations

import streamlit as st

from app.clients import auth_manager, http_client
from app.config import settings, validate_settings
from app.core.audit_engine import run_audit
from app.core.llm_client import (
    release_notes_summary,
    summarize_missing,
    suggest_regression_areas,
)
from app.core.rag_engine import build_corpus
from app.models import Commit, Issue


st.set_page_config(page_title="Release Audit", layout="wide")
APP_VERSION = "0.1.0"


def main():
    params = st.experimental_get_query_params()
    if params.get("healthz") == ["1"]:
        ok = not validate_settings(settings)
        st.write({"status": "ok", "config_ok": ok, "version": APP_VERSION})
        return

    st.title("RAG-Based Release Audit")

    errors = validate_settings(settings)
    if errors:
        st.error("\n".join(errors))

    with st.expander("Configuration"):
        st.write(
            {
                "jira_base_url": settings.jira_base_url,
                "bitbucket_base_url": settings.bitbucket_base_url,
                "default_repos": settings.default_bitbucket_repos,
                "default_branches": settings.default_branches,
                "ca_verify": http_client._resolve_verify(),
            }
        )

    with st.expander("Connection Status"):
        if st.button("Test Jira"):
            try:
                headers = auth_manager.jira_auth_header()
                url = f"{settings.jira_base_url}/rest/api/3/myself"
                data = http_client.request_json("GET", url, headers=headers)
                st.success(f"✅ {data.get('displayName')}")
            except Exception as exc:
                st.error(f"❌ {exc}")
        if st.button("Test Bitbucket"):
            try:
                headers = {"Authorization": f"Bearer {settings.bitbucket_token}"}
                project = (
                    settings.default_bitbucket_repos[0].split("/")[0]
                    if settings.default_bitbucket_repos
                    else ""
                )
                url = f"{settings.bitbucket_base_url}/rest/api/1.0/projects/{project}/repos"
                http_client.request_json(
                    "GET", url, headers=headers, params={"limit": 1}
                )
                st.success("✅")
            except Exception as exc:
                st.error(f"❌ {exc}")

    if "repos" not in st.session_state:
        st.session_state["repos"] = settings.default_bitbucket_repos
    if "branches" not in st.session_state:
        st.session_state["branches"] = settings.default_branches

    jql = st.text_area("JQL Query", value=settings.jira.jql_default)
    repos = st.multiselect(
        "Repositories",
        options=settings.default_bitbucket_repos,
        default=st.session_state["repos"],
        key="repos",
    )
    branches_text = st.text_input(
        "Branches (comma separated)",
        ",".join(st.session_state["branches"]),
    )
    branches = [b.strip() for b in branches_text.split(",") if b.strip()]
    st.session_state["branches"] = branches

    start = st.date_input("Start date", value=None)
    end = st.date_input("End date", value=None)
    refresh = st.checkbox("Refresh Data")
    run = st.button("Run audit")
    if not run or not jql:
        st.info("Enter parameters and run the audit")
        return
    repo_pairs = [(r, b) for r in repos for b in branches]
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
