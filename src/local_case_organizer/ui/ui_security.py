"""Basic same-origin safeguards for the single-user local browser interface.

This is browser CSRF mitigation, NOT network authentication or a multi-user ACL.
The app remains bound to loopback, and must not be exposed via public proxies.
"""
from __future__ import annotations

from urllib.parse import urlsplit


def allow_local_post(headers) -> bool:
    """Reject cross-site browser requests and all form/simple-header POSTs."""
    if headers.get("X-LCO-UI") != "same-origin-ui":
        return False
    site = headers.get("Sec-Fetch-Site", "")
    if site not in ("", "same-origin", "none"):
        return False
    origin = headers.get("Origin")
    if origin is not None:
        parsed = urlsplit(origin)
        host = str(headers.get("Host", ""))
        if parsed.scheme not in ("http", "https") or not parsed.netloc or (
            parsed.netloc.casefold() != host.casefold()
        ):
            return False
    return True


def allowed_ui_host(host: str) -> bool:
    return host in {"127.0.0.1", "::1", "localhost"}
