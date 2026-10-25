from __future__ import annotations

import csv
import hashlib

from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.register.store import write_register_rows
from local_case_organizer.timeline.store import read_timeline_rows
from local_case_organizer.timeline.suggestions import accept_candidate, propose_events


def _source(root, id_, name, content):
    p = paths.create_local_workspace(root)
    place = p.originals_dir / "batch" / name
    place.parent.mkdir(parents=True, exist_ok=True)
    place.write_bytes(content)
    provenance = p.register_dir / "provenance.csv"
    existing = []
    if provenance.exists():
        with provenance.open("r", encoding="utf-8", newline="") as fd:
            existing = list(csv.DictReader(fd))
    with provenance.open("w", encoding="utf-8", newline="") as fd:
        fields = ["file_id", "stored_relative_path", "sha256", "original_name"]
        writer = csv.DictWriter(fd, fieldnames=fields)
        writer.writeheader()
        for row in existing:
            writer.writerow(row)
        writer.writerow({"file_id": id_, "stored_relative_path": "batch/" + name,
                         "sha256": hashlib.sha256(content).hexdigest(), "original_name": name})
    return place


def test_suggestions_are_read_only_and_manual_draft(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    create_case(root, "alpha")
    with using_case("alpha"):
        _source(root, "DOC-1", "note.txt", b"Meeting on 2026-10-24 with Alice.\nPayment 25.10.2026 due.\n")
        write_register_rows([{"file_id": "DOC-1", "original_name": "note.txt"}])
        report = propose_events()
        assert [x["date"] for x in report["candidates"]] == ["2026-10-24", "2026-10-25"]
        assert read_timeline_rows() == []
        first = report["candidates"][0]
        saved = accept_candidate(first["candidate_id"])
        assert saved["status"] == "draft_added"
        assert accept_candidate(first["candidate_id"])["status"] == "already_recorded"
        timeline = read_timeline_rows()
        assert len(timeline) == 1
        assert timeline[0]["linked_file_ids"] == "DOC-1"
        assert timeline[0]["status"] == "draft"


def test_modified_original_not_used_for_event(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    p = _source(root, "DOC-1", "note.txt", b"2026-10-24 important")
    write_register_rows([{"file_id": "DOC-1", "original_name": "note.txt"}])
    item = propose_events()["candidates"][0]
    p.write_bytes(b"2026-10-24 changed")
    import pytest
    with pytest.raises(ValueError, match="unavailable"):
        accept_candidate(item["candidate_id"])
    assert read_timeline_rows() == []


def test_unsupported_invalid_dates_and_limit(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    _source(root, "DOC-1", "note.md", b"Invalid 31.02.2026 and valid 2026-01-05")
    _source(root, "DOC-2", "invoice.pdf", b"2026-02-03")
    write_register_rows([{"file_id": "DOC-1", "original_name": "note.md"},
                         {"file_id": "DOC-2", "original_name": "invoice.pdf"}])
    result = propose_events()
    assert len(result["candidates"]) == 1
    assert result["candidates"][0]["date"] == "2026-01-05"


def test_duplicate_hashes_reported_without_silent_merge(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    _source(root, "DOC-1", "a.txt", b"Date: 2026-10-24")
    _source(root, "DOC-2", "b.txt", b"Date: 2026-10-24")
    write_register_rows([{"file_id": "DOC-1", "original_name": "a.txt"},
                         {"file_id": "DOC-2", "original_name": "b.txt"}])
    result = propose_events()
    assert len(result["candidates"]) == 2
    assert result["duplicate_content"][0]["file_ids"] == ["DOC-1", "DOC-2"]
