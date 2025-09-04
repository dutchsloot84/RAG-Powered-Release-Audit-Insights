from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.clients import rapid_auth
from app.models import RapidToken


def test_token_refresh(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    monkeypatch.setattr(rapid_auth, "TOKEN_PATH", token_path)
    expired = RapidToken(
        access_token="old",
        refresh_token="ref",
        expires_in=3600,
        obtained_at=datetime.utcnow() - timedelta(hours=2),
    )
    rapid_auth.save_tokens(expired)

    def fake_request_json(method, url, json_body=None, **kwargs):
        return {"access_token": "new", "refresh_token": "ref", "expires_in": 3600}

    monkeypatch.setattr(rapid_auth, "request_json", fake_request_json)
    fake_settings = SimpleNamespace(
        rapid_client_id="id", rapid_client_secret="secret", rapid_token_url="url"
    )
    monkeypatch.setattr(rapid_auth, "settings", fake_settings)

    token = rapid_auth.get_valid_access_token()
    assert token == "new"
