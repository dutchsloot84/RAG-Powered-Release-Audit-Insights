from __future__ import annotations

from typing import Any, Dict, Optional

import logging
import os
import pathlib

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


def _resolve_verify():
    """Resolve the certificate bundle path for TLS verification.

    Priority: explicit PEM_PATH if it exists -> REQUESTS_CA_BUNDLE/SSL_CERT_FILE -> True
    (system default bundle).
    """

    pem_path = os.getenv("PEM_PATH")
    if pem_path and pathlib.Path(pem_path).is_file():
        return pem_path
    if pem_path:
        logger.warning("PEM_PATH %s not found; using system CA bundle", pem_path)

    for env_var in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        val = os.getenv(env_var)
        if val and pathlib.Path(val).is_file():
            return val

    return True


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
) -> Any:
    verify = _resolve_verify()
    if verify is True:
        logger.debug("Using system CA bundle")
    else:
        logger.debug("Using CA bundle at %s", verify)

    response = requests.request(
        method,
        url,
        headers=headers,
        params=params,
        json=json_body,
        verify=verify,
        timeout=30,
    )
    if response.status_code >= 400:
        raise HttpError(f"HTTP {response.status_code}: {response.text}")
    if response.status_code == 204:
        return None
    return response.json()
