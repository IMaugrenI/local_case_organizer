from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import webbrowser
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from local_case_organizer.export.builder import build_export_package
from local_case_organizer.imports.ingest import import_sources
from local_case_organizer.paths import create_local_workspace, describe_workspace, get_workspace_paths
from local_case_organizer.register.generator import build_document_register
from local_case_organizer.timeline.generator import build_timeline_template


HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>local_case_organizer</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fb; color: #18212f; }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 24px; }
    .hero { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    h1 { margin-top: 0; }
    .lead { color: #4b5563; line-height: 1.5; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 20px; }
    .card { background: white; border-radius: 14px; padding: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    .value { font-size: 28px; font-weight: bold; margin-top: 8px; }
    .actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 20px; }
    button { border: 0; border-radius: 12px; padding: 14px 16px; font-size: 15px; cursor: pointer; background: #1f6feb; color: white; }
    button.secondary { background: #0f766e; }
    button.light { background: #475569; }
    button.ghost { background: #e5e7eb; color: #111827; }
    .paths { margin-top: 18px; background: #0f172a; color: #e2e8f0; border-radius: 14px; padding: 16px; overflow: auto; }
    pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
    .log { margin-top: 18px; background: #111827; color: #d1fae5; border-radius: 14px; padding: 16px; min-height: 180px; }
    .section-title { margin-top: 28px; margin-bottom: 10px; }
    .note { font-size: 14px; color: #6b7280; }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <h1>local_case_organizer</h1>
      <p class=\"lead\">A simple local front door for building a clean case dossier. Put files into your inbox, import them, build a register, build a timeline, and export a handoff package.</p>
      <p class=\"note\">This UI is local-only. Your private files stay on your machine.</p>
    </div>

    <h2 class=\"section-title\">Current status</h2>
    <div class=\"grid\" id=\"cards\"></div>

    <h2 class=\"section-title\">Main actions</h2>
    <div class=\"actions\">
      <button onclick=\"runAction('setup')\">1. Prepare workspace</button>
      <button class=\"secondary\" onclick=\"runAction('import')\">2. Import inbox files</button>
      <button onclick=\"runAction('build-register')\">3. Build register</button>
      <button onclick=\"runAction('build-timeline')\">4. Build timeline</button>
      <button class=\"secondary\" onclick=\"runAction('export-package')\">5. Build export package</button>
    </div>

    <h2 class=\"section-title\">Helpful actions</h2>
    <div class=\"actions\">
      <button class=\"ghost\" onclick=\"runAction('open-inbox')\">Open inbox folder</button>
      <button class=\"ghost\" onclick=\"runAction('open-exports')\">Open exports folder</button>
      <button class=\"light\" onclick=\"runAction('doctor')\">Run doctor</button>
      <button class=\"light\" onclick=\"refreshStatus()\">Refresh status</button>
    </div>

    <h2 class=\"section-title\">Local paths</h2>
    <div class=\"paths\"><pre id=\"paths\">Loading paths...</pre></div>

    <h2 class=\"section-title\">Activity log</h2>
    <div class=\"log\"><pre id=\"log\">Starting local_case_organizer UI...</pre></div>
  </div>

  <script>
    function appendLog(text) {
      const log = document.getElementById('log');
      log.textContent = `[${new Date().toLocaleTimeString()}] ${text}\n\n` + log.textContent;
    }

    function renderCards(data) {
      const cards = document.getElementById('cards');
      cards.innerHTML = '';
      const items = [
        ['Inbox files', data.inbox_file_count ?? 0],
        ['Imported originals', data.original_file_count ?? 0],
        ['Import batches', data.import_batches ?? 0],
        ['Register files', data.register_files ?? 0],
        ['Export packages', data.export_packages ?? 0],
      ];
      for (const [label, value] of items) {
        const el = document.createElement('div');
        el.className = 'card';
        el.innerHTML = `<div>${label}</div><div class=\"value\">${value}</div>`;
        cards.appendChild(el);
      }
    }

    async function refreshStatus() {
      const response = await fetch('/api/status');
      const data = await response.json();
      renderCards(data.summary);
      document.getElementById('paths').textContent = JSON.stringify(data.paths, null, 2);
      appendLog('Status refreshed.');
    }

    async function runAction(action) {
      appendLog(`Running ${action} ...`);
      const response = await fetch(`/api/${action}`, { method: 'POST' });
      const data = await response.json();
      appendLog(JSON.stringify(data, null, 2));
      await refreshStatus();
    }

    refreshStatus();
  </script>
</body>
</html>
"""


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())



def _count_directories(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.iterdir() if item.is_dir())



def _check_writable(path: Path) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    probe = path / ".write_probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False



def _status_payload() -> dict[str, object]:
    paths = get_workspace_paths()
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "summary": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "inbox_file_count": _count_files(paths.inbox_dir),
            "original_file_count": _count_files(paths.originals_dir),
            "import_batches": _count_directories(paths.originals_dir),
            "register_files": _count_files(paths.register_dir),
            "export_packages": _count_directories(paths.exports_dir),
        },
        "paths": describe_workspace(paths),
    }



def _doctor_payload() -> dict[str, object]:
    paths = create_local_workspace()
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "checks": {
            "repo_root_exists": paths.repo_root.exists(),
            "run_py_exists": (paths.repo_root / "run.py").exists(),
            "src_package_exists": (paths.repo_root / "src" / "local_case_organizer").exists(),
            "data_dir_writable": _check_writable(paths.data_dir),
            "inbox_dir_writable": _check_writable(paths.inbox_dir),
            "originals_dir_writable": _check_writable(paths.originals_dir),
            "register_dir_writable": _check_writable(paths.register_dir),
            "exports_dir_writable": _check_writable(paths.exports_dir),
            "logs_dir_writable": _check_writable(paths.logs_dir),
        },
    }



def _open_path_in_file_manager(path: Path) -> dict[str, object]:
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
        return {"opened": str(path)}
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": str(exc), "path": str(path)}



def _json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, indent=2).encode("utf-8")



def run_ui(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> int:
    create_local_workspace()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, content_type: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._send(200, "text/html; charset=utf-8", HTML.encode("utf-8"))
                return
            if parsed.path == "/api/status":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_status_payload()))
                return
            self._send(404, "application/json; charset=utf-8", _json_bytes({"error": "not found"}))

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/setup":
                payload = {"created": describe_workspace(create_local_workspace())}
            elif parsed.path == "/api/import":
                payload = import_sources(None)
            elif parsed.path == "/api/build-register":
                payload = {"register_path": str(build_document_register())}
            elif parsed.path == "/api/build-timeline":
                payload = {"timeline_path": str(build_timeline_template())}
            elif parsed.path == "/api/export-package":
                payload = {"export_dir": str(build_export_package())}
            elif parsed.path == "/api/open-inbox":
                payload = _open_path_in_file_manager(get_workspace_paths().inbox_dir)
            elif parsed.path == "/api/open-exports":
                payload = _open_path_in_file_manager(get_workspace_paths().exports_dir)
            elif parsed.path == "/api/doctor":
                payload = _doctor_payload()
            else:
                self._send(404, "application/json; charset=utf-8", _json_bytes({"error": "not found"}))
                return

            self._send(200, "application/json; charset=utf-8", _json_bytes(payload))

        def log_message(self, fmt: str, *args: object) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print(json.dumps({"ui_url": url, "message": "local_case_organizer UI is running"}, indent=2))
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
