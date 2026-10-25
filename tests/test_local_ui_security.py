from __future__ import annotations

from local_case_organizer.cases import validate_case_id
from local_case_organizer.ui.ui_security import allow_local_post, allowed_ui_host
import pytest


def test_browser_post_must_be_same_origin_and_custom_header():
    good = {"Host":"127.0.0.1:8765", "Origin":"http://127.0.0.1:8765",
            "X-LCO-UI":"same-origin-ui", "Sec-Fetch-Site":"same-origin"}
    assert allow_local_post(good)
    assert not allow_local_post({**good, "Origin":"http://evil.invalid"})
    assert not allow_local_post({**good, "Sec-Fetch-Site":"cross-site"})
    assert not allow_local_post({**good, "X-LCO-UI":""})
    assert not allow_local_post({"Host":"127.0.0.1:8765"})


def test_single_user_ui_bind_only_loopback():
    assert allowed_ui_host("127.0.0.1")
    assert allowed_ui_host("::1")
    assert not allowed_ui_host("0.0.0.0")
    assert not allowed_ui_host("192.168.1.10")


def test_reserved_case_id_rejected():
    with pytest.raises(ValueError, match="Reserved"):
        validate_case_id("legacy-default")


def test_browser_fetch_wrapper_sends_same_origin_post_header():
    from local_case_organizer.ui.app import HTML
    assert "headers.set('X-LCO-UI', 'same-origin-ui')" in HTML
