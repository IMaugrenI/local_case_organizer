from __future__ import annotations

import cgi
import json
import os
import platform
import shutil
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
    .upload-box { background: white; border-radius: 14px; padding: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); margin-top: 20px; }
    .upload-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    input[type=file] { max-width: 100%; }
    .hint { margin-top: 12px; color: #6b7280; font-size: 14px; }
    .next-step { margin-top: 18px; background: #ecfeff; border: 1px solid #a5f3fc; color: #164e63; border-radius: 14px; padding: 16px; }
    .file-list { margin-top: 18px; background: white; border-radius: 14px; padding: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    ul { margin: 8px 0 0 18px; padding: 0; }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <h1>local_case_organizer</h1>
      <p class=\"lead\">A simple local front door for building a clean case dossier. Add files, import them, build a register, build a timeline, and export a handoff package.</p>
      <p class=\"note\">This UI is local-only. Your private files stay on your machine.</p>
    </div>

    <div class=\"next-step\" id=\"next-step\">Loading next step...</div>

    <h2 class=\"section-title\">Current status</h2>
    <div class=\"grid\" id=\"cards\"></div>

    <h2 class=\"section-title\">Add files</h2>
    <div class=\"upload-box\">
      <div class=\"upload-row\">
        <input id=\"fileInput\" type=\"file\" multiple>
        <button class=\"secondary\" onclick=\"uploadFiles()\">Upload selected files to inbox</button>
        <button class=\"ghost\" onclick=\"runAction('open-inbox')\">Open inbox folder</button>
      </div>
      <div class=\"hint\">You can either upload files here or open the inbox folder and place files there yourself.</div>
    </div>

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
      <button class=\"ghost\" onclick=\"runAction('open-exports')\">Open exports folder</button>
      <button class=\"light\" onclick=\"runAction('doctor')\">Run doctor</button>
      <button class=\"light\" onclick=\"refreshStatus()\">Refresh status</button>
    </div>

    <h2 class=\"section-title\">Recent inbox files</h2>
    <div class=\"file-list\"><div id=\"recent-files\">Loading recent files...</div></div>

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

    function renderRecentFiles(items) {
      const root = document.getElementById('recent-files');
      if (!items || items.length === 0) {
        root.textContent = 'No files are currently waiting in the inbox.';
        return;
      }
      const html = ['<ul>'];
      for (const item of items) {
        html.push(`<li>${item}</li>`);
      }
      html.push('</ul>');
      root.innerHTML = html.join('');
    }

    function renderNextStep(text) {
      document.getElementById('next-step').textContent = text;
    }

    async function refreshStatus() {
      const response = await fetch('/api/status');
      const data = await response.json();
      renderCards(data.summary);
      renderRecentFiles(data.recent_inbox_files || []);
      renderNextStep(data.next_step || 'Use the main action buttons below.');
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

    async function uploadFiles() {
      const input = document.getElementById('fileInput');
      if (!input.files || input.files.length === 0) {
        appendLog('No files selected for upload.');
        return;
      }
      const form = new FormData();
      for (const file of input.files) {
        form.append('files', file, file.name);
      }
      appendLog(`Uploading ${input.files.length} file(s) to inbox ...`);
      const response = await fetch('/api/upload', { method: 'POST', body: form });
      const data = await response.json();
      appendLog(JSON.stringify(data, null, 2));
      input.value = '';
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



def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1



def _recent_inbox_files(inbox_dir: Path, limit: int = 8) -> list[str]:
    files = [path for path in inbox_dir.rglob("*") if path.is_file()]
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return [str(path.relative_to(inbox_dir)) for path in files[:limit]]



def _next_step_message(paths: object) -> str:
    workspace_paths = get_workspace_paths()
    inbox_files = _count_files(workspace_paths.inbox_dir)
    import_batches = _count_directories(workspace_paths.originals_dir)
    register_files = _count_files(workspace_paths.register_dir)
    export_packages = _count_directories(workspace_paths.exports_dir)
    if inbox_files > 0:
        return "Next step: click 'Import inbox files' to move your waiting files into a tracked import batch."
    if import_batches == 0:
        return "Next step: add files through the upload box or open the inbox folder and place files there."
    if register_files == 0:
        return "Next step: click 'Build register' to create your document register."
    if export_packages == 0:
        return "Next step: build a timeline or create your first export package."
    return "Your workspace already has imports, register data, and exports. Use the buttons below for the next update cycle."



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
        "recent_inbox_files": _recent_inbox_files(paths.inbox_dir),
        "next_step": _next_step_message(paths),
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



def _save_uploaded_files(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    paths = create_local_workspace()
    form = cgi.FieldStorage(
        fp=handler.rfile,
        headers=handler.headers,
        environ={
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": handler.headers.get("Content-Type", ""),
        },
    )
    files_field = form["files"] if "files" in form else []
    if not isinstance(files_field, list):
        files_field = [files_field]

    saved: list[str] = []
    for item in files_field:
        filename = Path(item.filename or "uploaded_file").name
        target = _next_available_path(paths.inbox_dir / filename)
        with target.open("wb") as handle:
            shutil.copyfileobj(item.file, handle)
        saved.append(str(target.relative_to(paths.inbox_dir)))

    return {
        "uploaded_files": saved,
        "inbox_dir": str(paths.inbox_dir),
        "message": f"Saved {len(saved)} file(s) to the inbox.",
    }



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
            elif parsed.path == "/api/upload":
                payload = _save_uploaded_files(self)
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
