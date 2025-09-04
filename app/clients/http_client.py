from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings


class HttpError(Exception):
    pass


@retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(HttpError),
)
def request_json(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    pem_path: Optional[str] = None,
) -> Any:
    verify_path = pem_path or settings.pem_path
    response = requests.request(
        method,
        url,
        headers=headers,
        params=params,
        json=json_body,
        verify=verify_path,
        timeout=30,
    )
    if response.status_code >= 400:
        raise HttpError(f"HTTP {response.status_code}: {response.text}")
    if response.status_code == 204:
        return None
    return response.json()
