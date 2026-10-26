"""Regression for the browser boot script and local case-creation endpoint.

Previous UI changes passed Python-only tests despite a JavaScript syntax error
in the original HTML, disabling the fetch header wrapper and case creation.
"""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

from local_case_organizer.ui import app as ui


class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.inside = tag == "script" and not attrs.get("src") and (
            attrs.get("type", "text/javascript") in {"text/javascript", "module"}
        )
        if self.inside:
            self.scripts.append("")

    def handle_data(self, data):
        if self.inside:
            self.scripts[-1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False


def test_effective_entrypoint_scripts_are_valid_javascript():
    """Parse *rendered* entrypoint HTML, not standalone Python source strings."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node unavailable for JavaScript parser smoke")
    script = """
import run
import local_case_organizer.ui.app as ui
print(ui.run_ui.__globals__["HTML"])
"""
    repo = Path(__file__).resolve().parents[1]
    rendered = subprocess.run(
        [sys.executable, "-c", script], cwd=repo, check=True,
        capture_output=True, text=True, timeout=20,
    ).stdout
    parser = InlineScripts()
    parser.feed(rendered)
    assert len(parser.scripts) >= 4
    for index, js in enumerate(parser.scripts):
        checked = subprocess.run(
            [node, "--check"], input=js, capture_output=True,
            text=True, timeout=15,
        )
        assert checked.returncode == 0, (
            f"inline script #{index} cannot run:\n{checked.stderr}"
        )
    assert 'const originalCaseFetch = window.fetch.bind(window)' in rendered
    assert "headers.set('X-LCO-UI', 'same-origin-ui')" in rendered


def test_create_case_post_creates_isolated_test_case(tmp_path, monkeypatch):
    """No real data touched and no live HTTP server started."""
    monkeypatch.setattr(ui, "create_local_workspace", lambda *a, **kw: None)
    monkeypatch.setattr(ui, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(ui, "get_active_case", lambda: None)

    handlers = []
    class FakeServer:
        def __init__(self, _bind, handler):
            handlers.append(handler)
        def serve_forever(self):
            pass
        def server_close(self):
            pass

    monkeypatch.setattr(ui, "ThreadingHTTPServer", FakeServer)
    assert ui.run_ui(host="127.0.0.1", port=0, open_browser=False) == 0
    handler = object.__new__(handlers[0])
    payload = {"case_id": "testfall-2026", "title": "Testfall Oktober"}
    body = json.dumps(payload).encode()
    handler.path = "/api/create-case"
    handler.headers = {
        "Host": "127.0.0.1:8765",
        "Origin": "http://127.0.0.1:8765",
        "Sec-Fetch-Site": "same-origin",
        "X-LCO-UI": "same-origin-ui",
        "Content-Length": str(len(body)),
        "Content-Type": "application/json",
    }
    handler.rfile = io.BytesIO(body)
    sent = []
    handler._send = lambda code, mime, raw: sent.append((code, json.loads(raw)))
    handler.do_POST()
    assert sent[0][0] == 200, sent
    assert sent[0][1]["case_id"] == payload["case_id"]
    manifest = tmp_path / "cases" / "testfall-2026" / "case.json"
    assert manifest.exists()
    assert json.loads(manifest.read_text(encoding="utf-8"))["title"] == "Testfall Oktober"
    assert (manifest.parent / "data" / "inbox").is_dir()
