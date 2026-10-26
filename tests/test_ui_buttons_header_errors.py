"""B02 UI control audit and expected error responses (no real cases modified)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from local_case_organizer.ui import app as ui
from local_case_organizer.ui.local_case_organizer_ui_experience import EXPERIENCE_CSS
from local_case_organizer.ui.local_case_organizer_ui_theme_fixups import THEME_FIXUP_SCRIPT


def test_every_static_ui_button_has_a_javascript_handler():
    """Cover the HTML's existing 40 actions without executing destructive clicks."""
    html = ui.HTML
    handlers = re.findall(r'<button\b[^>]*\bonclick="([^"]+)"', html)
    assert len(handlers) >= 40
    available = set(re.findall(r'(?:async\s+)?function\s+([A-Za-z_]\w*)\s*\(', html))
    missing = []
    for handler in handlers:
        name = re.match(r'([A-Za-z_]\w*)\s*\(', handler)
        if not name or name.group(1) not in available:
            missing.append(handler)
    assert not missing, f"Buttons with missing callbacks: {missing}"


def test_all_main_buttons_have_valid_post_endpoints():
    html = ui.HTML
    post_handlers = re.findall(r"runAction\('([^']+)'\)", html)
    assert set(post_handlers) == {
        "setup", "import", "build-register", "build-timeline", "export-package",
        "open-inbox", "open-register", "open-exports", "doctor", "verify-integrity",
    }
    source = Path(ui.__file__).read_text(encoding="utf-8")
    for action in post_handlers:
        assert f'"/api/{action}"' in source, f"Missing API endpoint for {action}"
    assert "if (!response.ok)" in html


def test_hero_transparent_and_toolbar_is_global():
    assert "body .wrap .hero," in EXPERIENCE_CSS
    assert "background:transparent!important" in EXPERIENCE_CSS
    assert "background-image:none!important" in EXPERIENCE_CSS
    assert "position:sticky" in EXPERIENCE_CSS
    assert "#lco-brandbar .lco-top-toggles" in EXPERIENCE_CSS
    assert "header.appendChild(row)" in THEME_FIXUP_SCRIPT
    assert "row.appendChild(langButton)" in THEME_FIXUP_SCRIPT
    assert "row.appendChild(button)" in THEME_FIXUP_SCRIPT
    assert "updateHeaderHeight" in THEME_FIXUP_SCRIPT
    # Keep compact global controls legible and leave the language script intact.
    assert "min-height:40px!important" in EXPERIENCE_CSS
    assert "min-width:82px" in EXPERIENCE_CSS
    assert "font-size:.88rem!important" in EXPERIENCE_CSS
    assert "padding:8px 12px!important" in EXPERIENCE_CSS


def test_empty_import_is_json_400_not_thread_exception(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "create_local_workspace", lambda: None)
    monkeypatch.setattr(ui, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(ui, "get_active_case", lambda: None)
    def empty_import(*_args):
        raise ValueError("No files found to import")
    monkeypatch.setattr(ui, "import_sources", empty_import)

    servers = []
    class FakeServer:
        def __init__(self, _bind, handler_class):
            servers.append(handler_class)
        def serve_forever(self):
            pass
        def server_close(self):
            pass
    monkeypatch.setattr(ui, "ThreadingHTTPServer", FakeServer)
    assert ui.run_ui(host="127.0.0.1", port=0, open_browser=False) == 0
    handler = object.__new__(servers[0])
    handler.path = "/api/import"
    handler.headers = {
        "Host": "127.0.0.1:8765",
        "Origin": "http://127.0.0.1:8765",
        "X-LCO-UI": "same-origin-ui",
        "Sec-Fetch-Site": "same-origin",
        "Content-Length": "0",
    }
    sent = []
    handler._send = lambda status, content_type, body: sent.append((status, content_type, json.loads(body)))
    handler.do_POST()
    assert sent == [(400, "application/json; charset=utf-8",
                     {"error": "No files found to import"})]
