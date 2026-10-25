from __future__ import annotations

import csv
import hashlib
import json
from zipfile import ZipFile

import pytest

from local_case_organizer import paths
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.export.dossier import dossier_preview
from local_case_organizer.register.store import write_register_rows
from local_case_organizer.timeline.store import write_timeline_rows


def test_dossier_is_in_existing_verified_export(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    p = paths.create_local_workspace()
    original = p.originals_dir / "batch" / "proof.txt"
    original.parent.mkdir(parents=True)
    original.write_text("Important source", encoding="utf-8")
    sha = hashlib.sha256(original.read_bytes()).hexdigest()
    with (p.register_dir / "provenance.csv").open("w", encoding="utf-8", newline="") as fd:
        writer = csv.DictWriter(fd, fieldnames=["file_id","sha256","stored_relative_path","original_name"])
        writer.writeheader()
        writer.writerow({"file_id":"DOC-1","sha256":sha,"stored_relative_path":"batch/proof.txt",
                         "original_name":"proof.txt"})
    write_register_rows([{"file_id":"DOC-1","original_name":"proof.txt",
                          "selected_for_export":"yes","review_status":"reviewed"}])
    write_timeline_rows([{"event_id":"EV-1","event_date":"2026-10-25",
                          "event_title":"Proof arrived","linked_file_ids":"DOC-1","status":"draft"}])
    assert dossier_preview()["selected_documents"] == 1
    folder = build_export_package()
    dossier = (folder / "DOSSIER.md").read_text(encoding="utf-8")
    assert "Proof arrived" in dossier and "DOC-1" in dossier and sha in dossier
    with ZipFile(folder.with_suffix(".zip")) as z:
        names = z.namelist()
        assert {"DOSSIER.md", "EVIDENCE_INDEX.csv", "selected_originals/proof.txt"} <= set(names)
    manifest = json.loads((folder / "export_manifest.json").read_text(encoding="utf-8"))
    assert manifest["files_sha256"]["DOSSIER.md"] == hashlib.sha256((folder / "DOSSIER.md").read_bytes()).hexdigest()
    assert folder.with_suffix(".zip.sha256").is_file()


def test_no_selected_documents_still_yields_neutral_dossier(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    paths.create_local_workspace()
    write_register_rows([{"file_id":"DOC-2","original_name":"<script>",
                          "selected_for_export":"no"}])
    assert dossier_preview()["selected_documents"] == 0
    folder = build_export_package()
    content = (folder / "DOSSIER.md").read_text(encoding="utf-8")
    assert "<script>" not in content
    assert "0 selected attachment" in content


def test_integrity_mismatch_prevents_dossier_export(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    p = paths.create_local_workspace()
    source = p.originals_dir / "batch" / "wrong.txt"
    source.parent.mkdir(parents=True)
    source.write_text("original", encoding="utf-8")
    with (p.register_dir / "provenance.csv").open("w", encoding="utf-8", newline="") as fd:
        writer = csv.DictWriter(fd, fieldnames=["file_id","sha256","stored_relative_path","original_name"])
        writer.writeheader()
        writer.writerow({"file_id":"DOC-1","sha256":"0"*64,
                         "stored_relative_path":"batch/wrong.txt","original_name":"wrong.txt"})
    write_register_rows([{"file_id":"DOC-1","selected_for_export":"yes"}])
    with pytest.raises(ValueError, match="Integrity"):
        build_export_package()
