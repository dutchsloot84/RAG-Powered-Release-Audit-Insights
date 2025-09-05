#!/bin/sh
set -e

if [ ! -r "$PEM_PATH" ]; then
  echo "❌ PEM file not found or unreadable at $PEM_PATH" >&2
  exit 1
fi

echo "✅ PEM file accessible"

if curl --silent --fail --cacert "$PEM_PATH" "$JIRA_BASE_URL/rest/api/3/myself" >/dev/null; then
  echo "✅ Jira reachable"
else
  echo "❌ Jira unreachable" >&2
  exit 1
fi

if curl --silent --fail --cacert "$PEM_PATH" "$BITBUCKET_BASE_URL/rest/api/1.0/projects" >/dev/null; then
  echo "✅ Bitbucket reachable"
else
  echo "❌ Bitbucket unreachable" >&2
  exit 1
fi
