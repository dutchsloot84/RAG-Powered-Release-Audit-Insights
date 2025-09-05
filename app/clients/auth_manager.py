from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Dict, Optional

from app.config import settings


def _read_token_file(path: Path) -> Optional[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None


def jira_auth_header() -> Dict[str, str]:
    """Return Authorization header for Jira using OAuth token file or PAT."""
    if settings.jira_token_file:
        token = _read_token_file(Path(settings.jira_token_file)) or {}
        access = token.get("access_token")
        if access:
            return {"Authorization": f"Bearer {access}"}
    if settings.jira_email and settings.jira_api_token:
        creds = f"{settings.jira_email}:{settings.jira_api_token}".encode()
        b64 = base64.b64encode(creds).decode()
        return {"Authorization": f"Basic {b64}"}
    return {}
