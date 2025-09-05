# RAG-Powered Release Audit Insights

A release audit utility that cross-checks Jira issues against Bitbucket commits
within a JQL-defined window. The project provides a Streamlit UI, headless CLI
entry points, caching, and optional LLM-powered summaries.

> **Note**: GitHub support will be added in the future. The current version only
> integrates with Jira and Bitbucket.

## Features

- Fetch Jira issues using a user supplied JQL query
- Derive commit date window from issue activity
- Fetch Bitbucket commits across multiple repos/branches concurrently
- Match commit messages to Jira issue keys and report missing stories
- Optional RAG search and OpenAI summaries for missing stories, regression
  targets, and release notes
- Caching via JSON files and SQLite for repeatable, low-cost runs
- OAuth2 refresh logic for a placeholder "Rapid" API
- Docker and Streamlit based UI with export options

## Quick Start

```bash
cp .env.example .env  # populate tokens and base URLs
make install
make run  # launches Streamlit on http://localhost:8501
```

The Docker image includes the corporate CA bundle. `PEM_PATH` is optional and
only needed if you must override the system certificates.

### First Run Checklist

1. Fill in `.env` with Jira, Bitbucket, and OpenAI credentials.
2. `make run` or `docker compose up --build`.
3. In the UI, open **Configuration** and **Connection Status** to verify
   settings and connectivity.
4. Provide JQL, repositories, and branches, then run the audit.

### Example JQL

```
project = SRNGR AND fixVersion = "Mobilitas 2025.09.19" ORDER BY updated DESC
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `JIRA_BASE_URL` | Base URL to the Jira instance |
| `JIRA_EMAIL` | Jira account email for PAT auth |
| `JIRA_API_TOKEN` | Jira API token for PAT auth |
| `JIRA_TOKEN_FILE` | Path to Jira OAuth token JSON |
| `BITBUCKET_BASE_URL` | Bitbucket Server base URL |
| `BITBUCKET_TOKEN` | Bitbucket personal access token |
| `DEFAULT_BITBUCKET_REPOS` | Comma-separated repos `PROJECT/slug` |
| `DEFAULT_BRANCHES` | Comma-separated branches |
| `RAPID_TOKEN_URL` | OAuth2 token endpoint for Rapid API |
| `RAPID_CLIENT_ID` | OAuth2 client id |
| `RAPID_CLIENT_SECRET` | OAuth2 client secret |
| `OPENAI_API_KEY` | (Optional) OpenAI API key for LLM features |
| `OPENAI_MODEL` | OpenAI model name (default `gpt-4o-mini`) |
| `PEM_PATH` | (Optional) custom PEM to override system CA |

Example defaults:

```env
DEFAULT_BITBUCKET_REPOS=STARSYSONE/policycenter,STARSYSONE/claimcenter
DEFAULT_BRANCHES=develop,release/r-56.0
```

## Deriving the Audit Window

The audit window is calculated from the minimum and maximum `updated` timestamps
of all Jira issues returned by the JQL query, expanded by a buffer of seven
 days on each side. This window is then used to filter Bitbucket commits.

## CLI Usage

```bash
python main.py --jql "<JQL>" --repos "PROJ/repo:main" --headless
```

Results are written to `audit_results.json`. Use `--update-cache` to bypass
cache and force fresh API calls.

## Docker

```
docker-compose up --build
```

Mounts:
- `./cache` → `/app/cache`
- (Optional) mount `./corp.pem` → `/app/certs/corp.pem` and set `PEM_PATH`

## Testing & Linting

```
make lint
make test
```

## Troubleshooting

- If using a custom PEM, ensure the file exists and `PEM_PATH` points to it.
- Rate limit errors are automatically retried with backoff.
- FAISS is optional; installation may fail on unsupported platforms.

## Future Work

- Add GitHub integration parallel to Bitbucket.
- Enrich RAG index with file-level context.

MIT Licensed.
