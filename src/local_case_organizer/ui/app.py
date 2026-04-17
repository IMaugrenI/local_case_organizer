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

from local_case_organizer.entities.store import ENTITY_FIELDS, read_entity_rows, write_entity_rows
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.imports.ingest import import_sources
from local_case_organizer.paths import create_local_workspace, describe_workspace, get_workspace_paths
from local_case_organizer.register.generator import build_document_register
from local_case_organizer.register.store import REGISTER_FIELDS, read_register_rows, write_register_rows
from local_case_organizer.timeline.generator import build_timeline_template
from local_case_organizer.timeline.store import TIMELINE_FIELDS, read_timeline_rows, write_timeline_rows


HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>local_case_organizer</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fb; color: #18212f; }
    .wrap { max-width: 1280px; margin: 0 auto; padding: 24px; }
    .hero, .panel, .upload-box, .file-list, .paths, .log, .editor { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    .hero { padding: 24px; }
    h1, h2, h3 { margin-top: 0; }
    .lead { color: #4b5563; line-height: 1.5; }
    .note { font-size: 14px; color: #6b7280; }
    .section-title { margin-top: 28px; margin-bottom: 10px; }
    .next-step { margin-top: 18px; background: #ecfeff; border: 1px solid #a5f3fc; color: #164e63; border-radius: 14px; padding: 16px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 20px; }
    .card { background: white; border-radius: 14px; padding: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    .value { font-size: 28px; font-weight: bold; margin-top: 8px; }
    .actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 20px; }
    .upload-row, .editor-actions { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    button { border: 0; border-radius: 12px; padding: 14px 16px; font-size: 15px; cursor: pointer; background: #1f6feb; color: white; }
    button.secondary { background: #0f766e; }
    button.light { background: #475569; }
    button.ghost { background: #e5e7eb; color: #111827; }
    input[type=file] { max-width: 100%; }
    .hint { margin-top: 12px; color: #6b7280; font-size: 14px; }
    .paths, .log { margin-top: 18px; }
    .paths { background: #0f172a; color: #e2e8f0; overflow: auto; }
    .log { background: #111827; color: #d1fae5; min-height: 180px; }
    pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
    ul { margin: 8px 0 0 18px; padding: 0; }
    .editor { overflow: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 980px; }
    th, td { text-align: left; border-bottom: 1px solid #e5e7eb; padding: 10px; vertical-align: top; }
    th { background: #f8fafc; position: sticky; top: 0; }
    td.readonly { color: #475569; font-size: 13px; }
    input[type=text], textarea, select { width: 100%; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px; font: inherit; background: white; }
    textarea { min-height: 72px; resize: vertical; }
    .two-col { display: grid; grid-template-columns: 1fr; gap: 20px; }
    @media (min-width: 1100px) { .two-col { grid-template-columns: 1fr 1fr; } }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <h1>local_case_organizer</h1>
      <p class=\"lead\">A simple local front door for building a clean case dossier. Add files, import them, build a register, edit the working tables, and export a handoff package.</p>
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
      <button class=\"ghost\" onclick=\"runAction('open-register')\">Open register folder</button>
      <button class=\"ghost\" onclick=\"runAction('open-exports')\">Open exports folder</button>
      <button class=\"light\" onclick=\"runAction('doctor')\">Run doctor</button>
      <button class=\"light\" onclick=\"refreshAll()\">Refresh all</button>
    </div>

    <div class=\"two-col\">
      <div>
        <h2 class=\"section-title\">Document register</h2>
        <div class=\"editor\">
          <div class=\"editor-actions\">
            <button onclick=\"loadRegister()\">Load register</button>
            <button class=\"secondary\" onclick=\"saveRegister()\">Save register changes</button>
          </div>
          <div class=\"hint\">Editable fields are review status, document group, export selection, and note. The right-hand columns show where a file already appears in the timeline or entities table.</div>
          <div id=\"register-editor\" class=\"hint\">Register will appear here.</div>
        </div>
      </div>
      <div>
        <h2 class=\"section-title\">Timeline</h2>
        <div class=\"editor\">
          <div class=\"editor-actions\">
            <button onclick=\"loadTimeline()\">Load timeline</button>
            <button onclick=\"addTimelineRow()\">Add timeline row</button>
            <button class=\"secondary\" onclick=\"saveTimeline()\">Save timeline changes</button>
          </div>
          <div class=\"hint\">Use <code>linked_file_ids</code> to connect timeline events to file IDs from the register.</div>
          <div id=\"timeline-editor\" class=\"hint\">Timeline will appear here.</div>
        </div>
      </div>
    </div>

    <h2 class=\"section-title\">Entities / people / institutions</h2>
    <div class=\"editor\">
      <div class=\"editor-actions\">
        <button onclick=\"loadEntities()\">Load entities</button>
        <button onclick=\"addEntityRow()\">Add entity row</button>
        <button class=\"secondary\" onclick=\"saveEntities()\">Save entity changes</button>
      </div>
      <div class=\"hint\">Use <code>linked_file_ids</code> to connect people, institutions, or companies to file IDs from the register.</div>
      <div id=\"entity-editor\" class=\"hint\">Entities will appear here.</div>
    </div>

    <h2 class=\"section-title\">Recent inbox files</h2>
    <div class=\"file-list\"><div id=\"recent-files\">Loading recent files...</div></div>

    <h2 class=\"section-title\">Local paths</h2>
    <div class=\"paths\"><pre id=\"paths\">Loading paths...</pre></div>

    <h2 class=\"section-title\">Activity log</h2>
    <div class=\"log\"><pre id=\"log\">Starting local_case_organizer UI...</pre></div>
  </div>

  <script>
    let registerRows = [];
    let registerFields = [];
    let timelineRows = [];
    let timelineFields = [];
    let entityRows = [];
    let entityFields = [];

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
        ['Selected for export', data.selected_export_count ?? 0],
        ['Entities', data.entity_count ?? 0],
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

    function buildRegisterTable() {
      const root = document.getElementById('register-editor');
      if (!registerRows.length) {
        root.textContent = 'No register rows available yet. Build the register first.';
        return;
      }
      const html = ['<table><thead><tr>'];
      const visibleFields = ['file_id','original_name','relative_path','review_status','document_group','selected_for_export','linked_timeline_event_ids','linked_entity_ids','note'];
      for (const field of visibleFields) {
        html.push(`<th>${field}</th>`);
      }
      html.push('</tr></thead><tbody>');
      registerRows.forEach((row, index) => {
        html.push('<tr>');
        html.push(`<td class=\"readonly\">${row.file_id || ''}</td>`);
        html.push(`<td class=\"readonly\">${row.original_name || ''}</td>`);
        html.push(`<td class=\"readonly\">${row.relative_path || ''}</td>`);
        html.push(`<td><select data-register-row=\"${index}\" data-field=\"review_status\">` +
          ['unreviewed','reviewed','flagged','selected_for_export'].map(v => `<option value=\"${v}\" ${row.review_status === v ? 'selected' : ''}>${v}</option>`).join('') +
          '</select></td>');
        html.push(`<td><input type=\"text\" data-register-row=\"${index}\" data-field=\"document_group\" value=\"${escapeHtml(row.document_group || '')}\"></td>`);
        html.push(`<td><select data-register-row=\"${index}\" data-field=\"selected_for_export\">` +
          ['no','yes'].map(v => `<option value=\"${v}\" ${row.selected_for_export === v ? 'selected' : ''}>${v}</option>`).join('') +
          '</select></td>`);
        html.push(`<td class=\"readonly\">${escapeHtml(row.linked_timeline_event_ids || '')}</td>`);
        html.push(`<td class=\"readonly\">${escapeHtml(row.linked_entity_ids || '')}</td>`);
        html.push(`<td><textarea data-register-row=\"${index}\" data-field=\"note\">${escapeHtml(row.note || '')}</textarea></td>`);
        html.push('</tr>');
      });
      html.push('</tbody></table>');
      root.innerHTML = html.join('');
    }

    function buildTimelineTable() {
      const root = document.getElementById('timeline-editor');
      if (!timelineRows.length) {
        root.textContent = 'No timeline rows available yet. Build the timeline first.';
        return;
      }
      const html = ['<table><thead><tr>'];
      for (const field of timelineFields) {
        html.push(`<th>${field}</th>`);
      }
      html.push('</tr></thead><tbody>');
      timelineRows.forEach((row, index) => {
        html.push('<tr>');
        timelineFields.forEach(field => {
          const value = row[field] || '';
          if (field === 'summary') {
            html.push(`<td><textarea data-timeline-row=\"${index}\" data-field=\"${field}\">${escapeHtml(value)}</textarea></td>`);
          } else {
            html.push(`<td><input type=\"text\" data-timeline-row=\"${index}\" data-field=\"${field}\" value=\"${escapeHtml(value)}\"></td>`);
          }
        });
        html.push('</tr>');
      });
      html.push('</tbody></table>');
      root.innerHTML = html.join('');
    }

    function buildEntityTable() {
      const root = document.getElementById('entity-editor');
      if (!entityRows.length) {
        root.textContent = 'No entity rows available yet. Add your first row.';
        return;
      }
      const html = ['<table><thead><tr>'];
      for (const field of entityFields) {
        html.push(`<th>${field}</th>`);
      }
      html.push('</tr></thead><tbody>');
      entityRows.forEach((row, index) => {
        html.push('<tr>');
        entityFields.forEach(field => {
          const value = row[field] || '';
          if (field === 'notes') {
            html.push(`<td><textarea data-entity-row=\"${index}\" data-field=\"${field}\">${escapeHtml(value)}</textarea></td>`);
          } else {
            html.push(`<td><input type=\"text\" data-entity-row=\"${index}\" data-field=\"${field}\" value=\"${escapeHtml(value)}\"></td>`);
          }
        });
        html.push('</tr>');
      });
      html.push('</tbody></table>');
      root.innerHTML = html.join('');
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');
    }

    function syncRegisterFromInputs() {
      document.querySelectorAll('[data-register-row]').forEach(el => {
        const rowIndex = Number(el.getAttribute('data-register-row'));
        const field = el.getAttribute('data-field');
        registerRows[rowIndex][field] = el.value;
      });
    }

    function syncTimelineFromInputs() {
      document.querySelectorAll('[data-timeline-row]').forEach(el => {
        const rowIndex = Number(el.getAttribute('data-timeline-row'));
        const field = el.getAttribute('data-field');
        timelineRows[rowIndex][field] = el.value;
      });
    }

    function syncEntitiesFromInputs() {
      document.querySelectorAll('[data-entity-row]').forEach(el => {
        const rowIndex = Number(el.getAttribute('data-entity-row'));
        const field = el.getAttribute('data-field');
        entityRows[rowIndex][field] = el.value;
      });
    }

    async function loadRegister() {
      const response = await fetch('/api/register-data');
      const data = await response.json();
      registerFields = data.fields || [];
      registerRows = data.rows || [];
      buildRegisterTable();
      appendLog('Register loaded.');
    }

    async function saveRegister() {
      syncRegisterFromInputs();
      const response = await fetch('/api/save-register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: registerRows }),
      });
      const data = await response.json();
      appendLog(JSON.stringify(data, null, 2));
      await loadRegister();
      await refreshStatus();
    }

    async function loadTimeline() {
      const response = await fetch('/api/timeline-data');
      const data = await response.json();
      timelineFields = data.fields || [];
      timelineRows = data.rows || [];
      buildTimelineTable();
      appendLog('Timeline loaded.');
    }

    function addTimelineRow() {
      if (!timelineFields.length) {
        timelineFields = ['event_id','event_date','event_title','linked_file_ids','people_or_entities','summary','status'];
      }
      const nextId = `EV-${String(timelineRows.length + 1).padStart(6, '0')}`;
      const row = {
        event_id: nextId,
        event_date: '',
        event_title: '',
        linked_file_ids: '',
        people_or_entities: '',
        summary: '',
        status: 'draft',
      };
      timelineRows.push(row);
      buildTimelineTable();
      appendLog(`Added timeline row ${nextId}.`);
    }

    async function saveTimeline() {
      syncTimelineFromInputs();
      const response = await fetch('/api/save-timeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: timelineRows }),
      });
      const data = await response.json();
      appendLog(JSON.stringify(data, null, 2));
      await loadTimeline();
      await refreshStatus();
    }

    async function loadEntities() {
      const response = await fetch('/api/entity-data');
      const data = await response.json();
      entityFields = data.fields || [];
      entityRows = data.rows || [];
      buildEntityTable();
      appendLog('Entities loaded.');
    }

    function addEntityRow() {
      if (!entityFields.length) {
        entityFields = ['entity_id','entity_name','entity_type','linked_file_ids','notes'];
      }
      const nextId = `ENT-${String(entityRows.length + 1).padStart(6, '0')}`;
      entityRows.push({
        entity_id: nextId,
        entity_name: '',
        entity_type: '',
        linked_file_ids: '',
        notes: '',
      });
      buildEntityTable();
      appendLog(`Added entity row ${nextId}.`);
    }

    async function saveEntities() {
      syncEntitiesFromInputs();
      const response = await fetch('/api/save-entities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: entityRows }),
      });
      const data = await response.json();
      appendLog(JSON.stringify(data, null, 2));
      await loadEntities();
      await refreshStatus();
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
      await refreshAll();
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

    async function refreshAll() {
      await refreshStatus();
      await loadRegister();
      await loadTimeline();
      await loadEntities();
    }

    refreshAll();
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



def _selected_export_count() -> int:
    rows = read_register_rows()
    return sum(1 for row in rows if str(row.get("selected_for_export", "")).lower() == "yes")



def _split_link_values(value: str) -> list[str]:
    return [item.strip() for item in str(value).split(',') if item.strip()]



def _register_link_maps() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    timeline_map: dict[str, list[str]] = {}
    entity_map: dict[str, list[str]] = {}

    for row in read_timeline_rows():
        event_id = str(row.get("event_id", "")).strip()
        for file_id in _split_link_values(str(row.get("linked_file_ids", ""))):
            timeline_map.setdefault(file_id, []).append(event_id)

    for row in read_entity_rows():
        entity_id = str(row.get("entity_id", "")).strip()
        for file_id in _split_link_values(str(row.get("linked_file_ids", ""))):
            entity_map.setdefault(file_id, []).append(entity_id)

    return timeline_map, entity_map



def _next_step_message() -> str:
    workspace_paths = get_workspace_paths()
    inbox_files = _count_files(workspace_paths.inbox_dir)
    import_batches = _count_directories(workspace_paths.originals_dir)
    register_rows = len(read_register_rows())
    selected_for_export = _selected_export_count()
    export_packages = _count_directories(workspace_paths.exports_dir)
    if inbox_files > 0:
        return "Next step: use 'Import inbox files' to move your waiting files into a tracked import batch."
    if import_batches == 0:
        return "Next step: add files through the upload area or open the inbox folder and place files there."
    if register_rows == 0:
        return "Next step: use 'Build register' to create your document register."
    if selected_for_export == 0:
        return "Next step: mark the important register rows with 'selected_for_export = yes' so the handoff package knows what to include."
    if export_packages == 0:
        return "Next step: create your first export package."
    return "Your workspace already has imports, working tables, and exports. Use the browser tables to keep the dossier current."



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
            "selected_export_count": _selected_export_count(),
            "entity_count": len(read_entity_rows()),
            "export_packages": _count_directories(paths.exports_dir),
        },
        "paths": describe_workspace(paths),
        "recent_inbox_files": _recent_inbox_files(paths.inbox_dir),
        "next_step": _next_step_message(),
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
    except Exception as exc:
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



def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    return json.loads(raw.decode("utf-8")) if raw else {}



def _register_data_payload() -> dict[str, object]:
    timeline_map, entity_map = _register_link_maps()
    rows: list[dict[str, str]] = []
    for row in read_register_rows():
        file_id = str(row.get("file_id", "")).strip()
        enriched = dict(row)
        enriched["linked_timeline_event_ids"] = ", ".join(timeline_map.get(file_id, []))
        enriched["linked_entity_ids"] = ", ".join(entity_map.get(file_id, []))
        rows.append(enriched)
    return {"fields": REGISTER_FIELDS + ["linked_timeline_event_ids", "linked_entity_ids"], "rows": rows}



def _timeline_data_payload() -> dict[str, object]:
    build_timeline_template()
    return {"fields": TIMELINE_FIELDS, "rows": read_timeline_rows()}



def _entity_data_payload() -> dict[str, object]:
    return {"fields": ENTITY_FIELDS, "rows": read_entity_rows()}



def _save_register_payload(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    body = _read_json_body(handler)
    rows = body.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    path = write_register_rows(rows)
    return {"saved_register_path": str(path), "saved_rows": len(rows)}



def _save_timeline_payload(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    body = _read_json_body(handler)
    rows = body.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    path = write_timeline_rows(rows)
    return {"saved_timeline_path": str(path), "saved_rows": len(rows)}



def _save_entities_payload(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    body = _read_json_body(handler)
    rows = body.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    path = write_entity_rows(rows)
    return {"saved_entities_path": str(path), "saved_rows": len(rows)}



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

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._send(200, "text/html; charset=utf-8", HTML.encode("utf-8"))
                return
            if parsed.path == "/api/status":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_status_payload()))
                return
            if parsed.path == "/api/register-data":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_register_data_payload()))
                return
            if parsed.path == "/api/timeline-data":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_timeline_data_payload()))
                return
            if parsed.path == "/api/entity-data":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_entity_data_payload()))
                return
            self._send(404, "application/json; charset=utf-8", _json_bytes({"error": "not found"}))

        def do_POST(self) -> None:
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
            elif parsed.path == "/api/save-register":
                payload = _save_register_payload(self)
            elif parsed.path == "/api/save-timeline":
                payload = _save_timeline_payload(self)
            elif parsed.path == "/api/save-entities":
                payload = _save_entities_payload(self)
            elif parsed.path == "/api/export-package":
                export_dir = build_export_package()
                payload = {
                    "export_dir": str(export_dir),
                    "zip_path": str(export_dir.with_suffix('.zip')),
                    "manifest_path": str(export_dir / 'export_manifest.json'),
                }
            elif parsed.path == "/api/open-inbox":
                payload = _open_path_in_file_manager(get_workspace_paths().inbox_dir)
            elif parsed.path == "/api/open-register":
                payload = _open_path_in_file_manager(get_workspace_paths().register_dir)
            elif parsed.path == "/api/open-exports":
                payload = _open_path_in_file_manager(get_workspace_paths().exports_dir)
            elif parsed.path == "/api/doctor":
                payload = _doctor_payload()
            else:
                self._send(404, "application/json; charset=utf-8", _json_bytes({"error": "not found"}))
                return

            self._send(200, "application/json; charset=utf-8", _json_bytes(payload))

        def log_message(self, fmt: str, *args: object) -> None:
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
