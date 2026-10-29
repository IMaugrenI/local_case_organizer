"""Targeted one-page workflow checks; all writes use an isolated workspace."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from local_case_organizer import paths
from local_case_organizer.document_text import search_text
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.timeline.store import read_timeline_rows
from local_case_organizer.entities.store import read_entity_rows
from local_case_organizer.ui.quick_intake import quick_organize_inbox
from local_case_organizer.ui.simple_actions import (
    add_manual_entity,
    add_manual_event,
    prepare_local_search,
    update_document,
)
from local_case_organizer.ui.local_case_organizer_ui_workspace import WORKSPACE_SCRIPT
from local_case_organizer.ui.local_case_organizer_ui_specialist import SPECIALIST_SCRIPT


def test_one_page_pipeline_uses_existing_audited_stores(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    workspace = paths.create_local_workspace()
    source = workspace.inbox_dir / "memo.txt"
    source.write_text("Meeting on 01.06.2024 with Bob about a contract", encoding="utf-8")

    intake = quick_organize_inbox()
    assert intake["imported_files"] == 1
    rows = read_register_rows()
    assert len(rows) == 1
    file_id = rows[0]["file_id"]

    result = update_document({"file_id": file_id, "field": "selected_for_export", "value": "yes"})
    assert result["value"] == "yes"
    update_document({"file_id": file_id, "field": "note", "value": "Manual evaluation pending"})
    assert read_register_rows()[0]["note"] == "Manual evaluation pending"

    event = add_manual_event({
        "title": "Meeting noted", "date": "2024-06-01",
        "summary": "Unverified, entered by operator", "file_id": file_id,
    })
    assert event["status"] == "draft"
    events = read_timeline_rows()
    assert len(events) == 1
    assert events[0]["linked_file_ids"] == file_id
    assert events[0]["status"] == "draft"

    entity = add_manual_entity({"name": "Bob", "kind": "Person", "notes": "", "file_id": file_id})
    assert entity["entity_id"].startswith("EN-MAN-")
    assert read_entity_rows()[0]["linked_file_ids"] == file_id

    indexed = prepare_local_search(include_pdf=False)
    assert indexed["indexed"] == 1
    assert search_text("contract")["matches"][0]["file_id"] == file_id
    assert prepare_local_search(include_pdf=False)["already_indexed"] == 1

    assert source.exists()
    assert source.read_text(encoding="utf-8").startswith("Meeting on")
    assert read_register_rows()[0]["selected_for_export"] == "yes"


@pytest.mark.parametrize("payload", [
    {"file_id": "fake", "field": "selected_for_export", "value": "yes"},
    {"file_id": "fake", "field": "sha256", "value": "tamper"},
    {"file_id": "fake", "field": "selected_for_export", "value": "maybe"},
])
def test_document_patch_rejects_untrusted_or_unknown_fields(tmp_path, monkeypatch, payload):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    with pytest.raises(ValueError):
        update_document(payload)


def test_manual_timeline_rejects_unsupported_dates_and_unknown_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        add_manual_event({"title": "Short event", "date": "2026-13-45", "summary": "", "file_id": ""})
    with pytest.raises(ValueError, match="not in this case"):
        add_manual_event({"title": "Short event", "date": "2026-10-29", "summary": "", "file_id": "bogus"})


def test_one_page_shortcuts_do_not_leave_simple_mode():
    assert 'window.LCOOpenSimplePanel=openPanel' in WORKSPACE_SCRIPT
    for section in ("documents", "search", "timeline", "tasks", "entities", "handoff"):
        assert 'id="lco-ws-' + section + '"' in WORKSPACE_SCRIPT
    assert '"/api/quick-update-document"' in WORKSPACE_SCRIPT
    assert '"/api/quick-add-event"' in WORKSPACE_SCRIPT
    assert '"/api/quick-add-entity"' in WORKSPACE_SCRIPT
    assert '"/api/export-package"' in WORKSPACE_SCRIPT
    assert "window.confirm(fmt(\"exportConfirm\"" in WORKSPACE_SCRIPT
    assert '"/api/accept-candidate"' in WORKSPACE_SCRIPT
    assert "window.LCORefreshWorkspace=loadDocs" in WORKSPACE_SCRIPT


def test_specialist_tools_stay_collapsed_and_require_manual_actions():
    for name in ("claims", "comparisons", "ai", "ocr", "audit"):
        assert 'lco-special-' + name + '-pane' in SPECIALIST_SCRIPT
    assert 'window.confirm(t("aiConfirm"))' in SPECIALIST_SCRIPT
    assert 'window.confirm(t("ocrConfirm"))' in SPECIALIST_SCRIPT
    assert 'window.confirm(t("aiActionConfirm"))' in SPECIALIST_SCRIPT
    assert '"/api/prepare-ai-review"' in SPECIALIST_SCRIPT
    assert '"/api/review-ai-suggestion"' in SPECIALIST_SCRIPT
    assert '"/api/add-claim"' in SPECIALIST_SCRIPT
    assert '"/api/add-comparison"' in SPECIALIST_SCRIPT
    assert '"/api/index-document"' in SPECIALIST_SCRIPT
    assert "document.addEventListener(\"DOMContentLoaded\",init)" in SPECIALIST_SCRIPT


def test_runtime_entrypoint_contains_single_page_without_new_server():
    script = """
import run
import local_case_organizer.ui.app as ui
html = ui.run_ui.__globals__["HTML"]
assert 'lco-ws-documents' in html
assert 'lco-ws-integrity' in html
assert 'lco-ws-task-list' in html
assert 'lco-ws-entity-list' in html
assert 'lco-ws-timeline' in html
assert 'lco-ws-handoff' in html
assert 'lco-special-ai-pane' in html
assert 'lco-special-claims-pane' in html
print('ONE_PAGE_UI_OK')
"""
    result = subprocess.run([sys.executable, "-c", script],
                            cwd=Path(__file__).resolve().parents[1],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert "ONE_PAGE_UI_OK" in result.stdout
