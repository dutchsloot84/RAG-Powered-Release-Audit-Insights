from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from app.clients.http_client import request_json
from app.config import settings
from app.models import RapidToken

TOKEN_PATH = Path("cache/rapid_token.json")


def load_tokens() -> RapidToken | None:
    if not TOKEN_PATH.exists():
        return None
    with TOKEN_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return RapidToken(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=data["expires_in"],
        obtained_at=datetime.fromisoformat(data["obtained_at"]),
    )


def save_tokens(token: RapidToken) -> None:
    TOKEN_PATH.parent.mkdir(exist_ok=True)
    payload = token.model_dump()
    payload["obtained_at"] = token.obtained_at.isoformat()
    with TOKEN_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f)


def refresh_tokens(refresh_token: str) -> RapidToken:
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.rapid_client_id,
        "client_secret": settings.rapid_client_secret,
    }
    data = request_json("POST", settings.rapid_token_url, json_body=payload)
    token = RapidToken(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token", refresh_token),
        expires_in=int(data.get("expires_in", 3600)),
        obtained_at=datetime.utcnow(),
    )
    save_tokens(token)
    return token


def get_valid_access_token() -> str:
    token = load_tokens()
    if token and token.obtained_at + timedelta(seconds=token.expires_in - 60) > datetime.utcnow():
        return token.access_token
    if not token:
        raise RuntimeError("No Rapid token available; perform initial authentication")
    token = refresh_tokens(token.refresh_token)
    return token.access_token
