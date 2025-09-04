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
# place corporate certificate as corp.pem in project root
make install
make run  # launches Streamlit on http://localhost:8501
```

### Example JQL

```
project = SRNGR AND fixVersion = "Mobilitas 2025.09.19" ORDER BY updated DESC
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `JIRA_BASE_URL` | Base URL to the Jira instance |
| `JIRA_TOKEN` | Jira personal access token |
| `BITBUCKET_BASE_URL` | Bitbucket Server base URL |
| `BITBUCKET_TOKEN` | Bitbucket personal access token |
| `RAPID_TOKEN_URL` | OAuth2 token endpoint for Rapid API |
| `RAPID_CLIENT_ID` | OAuth2 client id |
| `RAPID_CLIENT_SECRET` | OAuth2 client secret |
| `OPENAI_API_KEY` | (Optional) OpenAI API key for LLM features |
| `OPENAI_MODEL` | OpenAI model name (default `gpt-4o-mini`) |
| `PEM_PATH` | Path to corporate PEM certificate |

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
- `./corp.pem` → `/app/certs/corp.pem`

## Testing & Linting

```
make lint
make test
```

## Troubleshooting

- Ensure the PEM certificate exists at the path specified by `PEM_PATH`.
- Rate limit errors are automatically retried with backoff.
- FAISS is optional; installation may fail on unsupported platforms.

## Future Work

- Add GitHub integration parallel to Bitbucket.
- Enrich RAG index with file-level context.

MIT Licensed.
