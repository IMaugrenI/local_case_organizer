"""A15 selected-only handoff readiness and safe ZIP content checks."""
from __future__ import annotations

import csv
import json
from zipfile import ZipFile

import pytest

from local_case_organizer import paths
from local_case_organizer.audit import write_audited_csv
from local_case_organizer.claims import CLAIM_FIELDS, add_claim, read_claims
from local_case_organizer.document_text import index_document
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.export.dossier import dossier_preview
from local_case_organizer.export.quality import handoff_quality
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.timeline.store import write_timeline_rows
from local_case_organizer.ui.quick_intake import quick_organize_inbox


def _fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    for name, body in {
        "selected.txt": "Aktenzeichen: 123-444\nAussage: 100 EUR\n",
        "private.txt": "SECRET-ONLY-8129\nAussage: 900 EUR\n",
    }.items():
        (workspace.inbox_dir / name).write_text(body, encoding="utf-8")
    assert quick_organize_inbox()["imported_files"] == 2
    rows = read_register_rows()
    docs = {row["original_name"]: row for row in rows}
    for row in rows:
        row["selected_for_export"] = "yes" if row["original_name"] == "selected.txt" else "no"
    write_register_rows(rows)
    for doc in docs.values():
        index_document(doc["file_id"])
    return workspace, docs


def test_quality_preview_is_selected_only_read_only_and_warning_aware(tmp_path, monkeypatch):
    workspace, docs = _fixture(tmp_path, monkeypatch)
    selected = docs["selected.txt"]["file_id"]
    private = docs["private.txt"]["file_id"]
    claim = add_claim(selected, 1, "Aussage: 100 EUR", "Source statement needs human review")
    add_claim(private, 1, "Aussage: 900 EUR", "SECRET-ONLY-8129")
    write_timeline_rows([
        {"event_id": "EV-SELECTED", "event_title": "Allowed case work",
         "event_date": "2025-01-01", "linked_file_ids": selected, "status": "draft"},
        {"event_id": "EV-MIXED", "event_title": "SECRET-ONLY-8129",
         "event_date": "2025-02-01", "linked_file_ids": selected + "," + private,
         "status": "draft"},
    ])
    before = {f.name: f.read_bytes() for f in workspace.register_dir.iterdir() if f.is_file()}
    report = handoff_quality()
    assert report["selected_documents"] == 1
    assert report["verified_originals"] == 1
    assert report["claims_in_selection"] == 1
    assert report["claims_quote_verified"] == 1
    assert report["included_timeline_entries"] == 1
    assert report["manual_review_pending_in_scan"] == 1
    assert private not in json.dumps(report)
    assert "SECRET-ONLY-8129" not in json.dumps(report)
    assert report["limits"]["no_external_data_completeness_claim"]
    assert dossier_preview()["claims_in_selection"] == 1
    assert before == {f.name: f.read_bytes() for f in workspace.register_dir.iterdir() if f.is_file()}

    folder = build_export_package()
    with ZipFile(folder.with_suffix(".zip")) as archive:
        names = set(archive.namelist())
        assert "UEBERGABE_PRUEFPUNKTE.md" in names
        assert "selected_originals/selected.txt" in names
        assert "selected_originals/private.txt" not in names
        for filename in names:
            if filename.endswith((".md", ".csv", ".json", ".txt")) and not filename.startswith("selected_originals/"):
                body = archive.read(filename).decode("utf-8")
                assert private not in body
                assert "SECRET-ONLY-8129" not in body
        assert "Allowed case work" in archive.read("timeline.csv").decode()
        assert "SECRET-ONLY-8129" not in archive.read("DOSSIER.md").decode()
    assert claim["claim_id"] in (folder / "claims.csv").read_text(encoding="utf-8")
    manifest = json.loads((folder / "export_manifest.json").read_text(encoding="utf-8"))
    assert "UEBERGABE_PRUEFPUNKTE.md" in manifest["files_sha256"]


def test_stale_claim_never_enters_selected_handoff(tmp_path, monkeypatch):
    workspace, docs = _fixture(tmp_path, monkeypatch)
    selected = docs["selected.txt"]["file_id"]
    claim = add_claim(selected, 1, "Aussage: 100 EUR", "Untrusted content not supported")
    claims = read_claims()
    claims[0]["source_quote"] = "UNVERIFIABLE PRIVATE CLAIM TEXT"
    write_audited_csv(workspace.register_dir / "claims.csv", CLAIM_FIELDS, claims, "claims")
    report = handoff_quality()
    assert report["claims_in_selection"] == 1
    assert report["claims_quote_verified"] == 0
    assert report["claims_excluded_unverifiable"] == 1
    folder = build_export_package()
    assert not (folder / "claims.csv").exists()
    for filename in ("DOSSIER.md", "UEBERGABE_PRUEFPUNKTE.md", "ANWALT_START_HERE.md"):
        body = (folder / filename).read_text(encoding="utf-8")
        assert "UNVERIFIABLE PRIVATE CLAIM TEXT" not in body
        assert "Untrusted content not supported" not in body
    assert claim["claim_id"] not in (folder / "DOSSIER.md").read_text(encoding="utf-8")


def test_missing_selected_original_blocks_before_creating_export(tmp_path, monkeypatch):
    workspace, docs = _fixture(tmp_path, monkeypatch)
    source = workspace.originals_dir / docs["selected.txt"]["relative_path"]
    source.unlink()
    preview = handoff_quality()
    assert preview["export_blocked_in_scanned_sources"]
    assert preview["originals_needing_attention"] == 1
    with pytest.raises(ValueError, match="Integrity"):
        build_export_package()
    assert list(workspace.exports_dir.iterdir()) == []


def test_quality_preview_limit_does_not_claim_all_sources_verified(tmp_path, monkeypatch):
    _workspace, _docs = _fixture(tmp_path, monkeypatch)
    import local_case_organizer.export.quality as quality
    monkeypatch.setattr(quality, "MAX_PREVIEW_SOURCES", 0)
    report = quality.handoff_quality()
    assert report["selected_documents"] == 1
    assert report["inspected_originals"] == 0
    assert report["verified_originals"] == 0
    assert report["not_scanned"] == 1
    assert report["complete_preview"] is False
    assert report["warnings"][0]["code"] == "preview_not_all_sources_scanned"


def test_user_must_confirm_warnings_in_existing_browser_export():
    from local_case_organizer.ui.local_case_organizer_ui_workspace import WORKSPACE_SCRIPT
    assert '"/api/dossier-preview"' in WORKSPACE_SCRIPT
    assert "lco-ws-quality-check" in WORKSPACE_SCRIPT
    assert "lco-ws-quality-summary" in WORKSPACE_SCRIPT
    assert 'if(quality.export_blocked_in_scanned_sources)' in WORKSPACE_SCRIPT
    assert 'window.confirm(fmt("qualityApprove"' in WORKSPACE_SCRIPT
    assert '"/api/export-package"' in WORKSPACE_SCRIPT
    assert "textContent" in WORKSPACE_SCRIPT
