"""Isolated review of selected-only lawyer handoff and read-only case briefing."""
from __future__ import annotations

import csv
import hashlib
from zipfile import ZipFile

from local_case_organizer import paths
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.timeline.store import write_timeline_rows
from local_case_organizer.ui.case_briefing import case_briefing
from local_case_organizer.ui.local_case_organizer_ui_briefing import BRIEFING_SCRIPT


def _source(paths_, name, contents, file_id):
    source = paths_.originals_dir / "batch" / name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(contents, encoding="utf-8")
    return {"batch_id": "IMP-test", "file_id": file_id,
            "original_name": name, "stored_relative_path": "batch/" + name,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "source_path": "/private/work/DO_NOT_EXPORT", "size_bytes": str(source.stat().st_size)}


def test_lawyer_bundle_excludes_unselected_metadata_and_includes_readme(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    public = _source(workspace, "allowed.txt", "Allowed original", "DOC-A")
    private = _source(workspace, "secret.txt", "TOP SECRET PRIVATE DATA", "DOC-B")
    with (workspace.register_dir / "provenance.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = list(public)
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows([public, private])
    write_register_rows([
        {"file_id": "DOC-A", "original_name": "allowed.txt", "selected_for_export": "yes",
         "review_status": "unreviewed", "note": "Need to check source"},
        {"file_id": "DOC-B", "original_name": "secret.txt", "selected_for_export": "no",
         "review_status": "flagged", "note": "TOP SECRET PRIVATE DATA"},
    ])
    write_timeline_rows([
        {"event_id": "EV-A", "event_date": "2020-01-01", "event_title": "Shared event",
         "linked_file_ids": "DOC-A,DOC-B", "status": "draft"},
        {"event_id": "EV-B", "event_date": "2021-01-01", "event_title": "TOP SECRET EVENT",
         "linked_file_ids": "DOC-B", "status": "draft"},
    ])
    folder = build_export_package()
    with ZipFile(folder.with_suffix(".zip")) as z:
        names = set(z.namelist())
        assert "ANWALT_START_HERE.md" in names
        assert "selected_originals/allowed.txt" in names
        assert "selected_originals/secret.txt" not in names
        for filename in ("provenance.csv", "document_register.csv", "timeline.csv", "DOSSIER.md", "ANWALT_START_HERE.md"):
            body = z.read(filename).decode("utf-8")
            assert "DOC-B" not in body
            assert "secret.txt" not in body
            assert "TOP SECRET" not in body
            assert "/private/work/" not in body
        assert "Shared event" in z.read("ANWALT_START_HERE.md").decode()
        assert "TOP SECRET EVENT" not in z.read("DOSSIER.md").decode()
    with (folder / "timeline.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
        assert rows[0]["linked_file_ids"] == "DOC-A"
    assert len(read_register_rows()) == 2
    assert private["sha256"] != public["sha256"]


def test_case_briefing_only_reports_review_hints_without_writing(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    write_register_rows([
        {"file_id": "DOC-ONE", "original_name": "memo.txt",
         "selected_for_export": "no", "review_status": "unreviewed"},
    ])
    before = (workspace.register_dir / "document_register.csv").read_bytes()
    overview = case_briefing()
    assert overview["totals"]["documents"] == 1
    assert overview["totals"]["review_pending"] == 1
    assert overview["totals"]["selected_export"] == 0
    assert overview["limitations"]["date_mentions_are_unverified"] is True
    assert (workspace.register_dir / "document_register.csv").read_bytes() == before


def test_briefing_copy_avoids_claiming_legal_assessment_or_automatic_approval():
    assert "case-briefing" in BRIEFING_SCRIPT
    assert "lco-brief-handoff" in BRIEFING_SCRIPT
    assert "lco-ws-handoff" in BRIEFING_SCRIPT
    assert "keine bewiesenen Tatsachen" in BRIEFING_SCRIPT
    assert "Keine automatische rechtliche Fristberechnung" in BRIEFING_SCRIPT
