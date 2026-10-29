"""Autopilot regression suite: isolated case data, no external tools required."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from local_case_organizer import document_text, paths
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.timeline.store import read_timeline_rows
from local_case_organizer.timeline.suggestions import accept_candidate, propose_events
from local_case_organizer.ui.autopilot import autopilot_status, process_autopilot
from local_case_organizer.ui.quick_intake import quick_organize_inbox


def _local(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    return paths.create_local_workspace()


def test_autopilot_indexes_plaintext_and_queues_optional_ocr(tmp_path, monkeypatch):
    area = _local(tmp_path, monkeypatch)
    (area.inbox_dir / "brief.txt").write_text(
        "Gericht: Termin am 21.01.2023. Nicht bestaetigt.", encoding="utf-8",
    )
    (area.inbox_dir / "scan.png").write_bytes(b"synthetic image placeholder")
    (area.inbox_dir / "other.xyz").write_bytes(b"unsupported contents")
    assert quick_organize_inbox()["imported_files"] == 3
    originals = {
        path.relative_to(area.originals_dir): path.read_bytes()
        for path in area.originals_dir.rglob("*") if path.is_file()
    }
    first = process_autopilot()
    assert first["total"] == 3
    assert first["indexed"] == 1
    assert first["needs_ocr"] == 1
    assert first["skipped"] == 1
    assert first["remaining"] == 0
    assert first["manual_review_required"] is True
    snapshot = autopilot_status()
    assert snapshot["indexed"] == 1
    assert snapshot["needs_ocr"] == 1
    assert process_autopilot()["processed_in_batch"] == 0
    assert list(area.working_dir.glob("autopilot_state.json"))
    assert all(path.read_bytes() == original for relative, original in originals.items()
               for path in [area.originals_dir / relative])
    candidates = propose_events()["candidates"]
    assert any(item["date"] == "2023-01-21" for item in candidates)
    assert read_timeline_rows() == []


def test_autopilot_rebuilds_index_if_original_is_new_digest(tmp_path, monkeypatch):
    area = _local(tmp_path, monkeypatch)
    (area.inbox_dir / "case.txt").write_text("First filing", encoding="utf-8")
    quick_organize_inbox()
    file_id = read_register_rows()[0]["file_id"]
    assert process_autopilot()["indexed"] == 1
    derived = document_text.get_indexed(file_id, verify_original=True)
    assert "First" in derived["pages"][0]["text"]

    # A broken original is never silently repaired or overwritten.
    original = area.originals_dir / read_register_rows()[0]["relative_path"]
    original.write_text("Tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity"):
        document_text.get_indexed(file_id, verify_original=True)
    assert original.read_text(encoding="utf-8") == "Tampered"


def test_pdf_date_suggestions_use_verified_indexed_pages_only(tmp_path, monkeypatch):
    area = _local(tmp_path, monkeypatch)
    fake_pdf = area.inbox_dir / "letter.pdf"
    fake_pdf.write_bytes(b"%PDF fixture text never parsed")
    assert quick_organize_inbox()["imported_files"] == 1
    row = read_register_rows()[0]
    path = document_text._index_path(row["file_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "version": 1,
        "file_id": row["file_id"],
        "source_sha256": row["sha256"],
        "pages": [
            {"page": 1, "text": "No dates"},
            {"page": 2, "text": "Schreiben vom 04.05.2022: unverified text."},
        ],
    }), encoding="utf-8")
    proposal = propose_events()
    assert len(proposal["candidates"]) == 1
    suggestion = proposal["candidates"][0]
    assert suggestion["date"] == "2022-05-04"
    assert suggestion["page"] == 2
    assert suggestion["review_status"] == "suggested_not_verified"
    assert read_timeline_rows() == []
    accepted = accept_candidate(suggestion["candidate_id"])
    assert accepted["status"] == "draft_added"
    assert read_timeline_rows()[0]["status"] == "draft"
    assert accept_candidate(suggestion["candidate_id"])["status"] == "already_recorded"
    original = area.originals_dir / row["relative_path"]
    original.write_bytes(b"modified private source")
    after = propose_events()
    assert after["candidates"] == []
    assert any(w["file_id"] == row["file_id"] for w in after["warnings"])


def test_autopilot_resumes_multiple_batches_and_separates_cases(tmp_path, monkeypatch):
    from local_case_organizer.cases import create_case, using_case

    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    create_case(tmp_path, "synthetic-a", "Synthetic A")
    create_case(tmp_path, "synthetic-b", "Synthetic B")
    with using_case("synthetic-a"):
        area = paths.create_local_workspace()
        for index in range(10):
            (area.inbox_dir / ("text-%02d.txt" % index)).write_text(
                "Sample %d" % index, encoding="utf-8")
        assert quick_organize_inbox()["imported_files"] == 10
        assert process_autopilot()["indexed"] == 4
        assert process_autopilot()["indexed"] == 8
        third = process_autopilot()
        assert third["indexed"] == 10
        assert third["remaining"] == 0
        assert process_autopilot()["processed_in_batch"] == 0
        assert (area.working_dir / "autopilot_state.json").exists()
    with using_case("synthetic-b"):
        assert autopilot_status()["total"] == 0
        assert autopilot_status()["indexed"] == 0
        area_b = paths.create_local_workspace()
        assert not (area_b.working_dir / "autopilot_state.json").exists()


def test_processing_journal_refuses_symlink_and_preserves_target(tmp_path, monkeypatch):
    area = _local(tmp_path, monkeypatch)
    outside = tmp_path / "outside.json"
    outside.write_text("do not modify", encoding="utf-8")
    (area.working_dir / "autopilot_state.json").symlink_to(outside)
    with pytest.raises(ValueError, match="journal"):
        process_autopilot()
    assert outside.read_text(encoding="utf-8") == "do not modify"


def test_autopilot_ui_is_in_existing_local_entrypoint():
    from local_case_organizer.ui.local_case_organizer_ui_autopilot import AUTOPILOT_SCRIPT
    assert '"/api/autopilot-process"' in AUTOPILOT_SCRIPT
    assert '"/api/autopilot-status"' in AUTOPILOT_SCRIPT
    assert 'use_ocr:useOcr' in AUTOPILOT_SCRIPT
    assert 'window.LCOAutopilot={runAfterImport' in AUTOPILOT_SCRIPT
