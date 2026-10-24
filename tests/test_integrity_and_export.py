from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

from local_case_organizer.export import helpers
from local_case_organizer.imports import ingest
from local_case_organizer.paths import create_local_workspace


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_back_to_back_imports_get_unique_ids(tmp_path, monkeypatch):
    paths = create_local_workspace(tmp_path / "repo")
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("alpha", encoding="utf-8")

    monkeypatch.setattr(ingest, "create_local_workspace", lambda: paths)

    first = ingest.import_sources(str(source))
    second = ingest.import_sources(str(source))

    assert first["batch_id"] != second["batch_id"]

    first_manifest = Path(first["manifest_path"])
    second_manifest = Path(second["manifest_path"])
    with first_manifest.open("r", encoding="utf-8", newline="") as handle:
        first_id = next(csv.DictReader(handle))["file_id"]
    with second_manifest.open("r", encoding="utf-8", newline="") as handle:
        second_id = next(csv.DictReader(handle))["file_id"]

    assert first_id != second_id
    assert first_manifest != second_manifest


def test_symlink_escape_is_not_imported(tmp_path, monkeypatch):
    paths = create_local_workspace(tmp_path / "repo")
    source = tmp_path / "source"
    source.mkdir()
    (source / "inside.txt").write_text("inside", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")

    link = source / "outside-link.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlinks are unavailable in this environment")

    monkeypatch.setattr(ingest, "create_local_workspace", lambda: paths)
    result = ingest.import_sources(str(source))

    assert result["imported_files"] == 1


def _write_provenance(paths, *, file_id: str, stored_relative_path: str, digest: str, source_path: str = "/private/home/file.txt"):
    provenance = paths.register_dir / "provenance.csv"
    with provenance.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ingest.MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "batch_id": "IMP-test",
                "file_id": file_id,
                "imported_at_utc": "2026-01-01T00:00:00+00:00",
                "source_label": "cli-source",
                "source_path": source_path,
                "original_name": "file.txt",
                "stored_relative_path": stored_relative_path,
                "sha256": digest,
                "size_bytes": "4",
            }
        )


def test_export_rejects_path_escape(tmp_path, monkeypatch):
    paths = create_local_workspace(tmp_path / "repo")
    outside = tmp_path / "outside.txt"
    outside.write_text("data", encoding="utf-8")
    _write_provenance(paths, file_id="DOC-1", stored_relative_path="../outside.txt", digest=sha256(outside))

    monkeypatch.setattr(helpers, "get_workspace_paths", lambda: paths)
    monkeypatch.setattr(
        helpers,
        "read_register_rows",
        lambda: [{"file_id": "DOC-1", "selected_for_export": "yes"}],
    )

    export_dir = paths.exports_dir / "export"
    export_dir.mkdir()
    with pytest.raises(ValueError, match="escapes originals directory"):
        helpers.copy_selected_files(export_dir)


def test_export_rejects_hash_mismatch(tmp_path, monkeypatch):
    paths = create_local_workspace(tmp_path / "repo")
    original = paths.originals_dir / "IMP-test" / "file.txt"
    original.parent.mkdir(parents=True)
    original.write_text("changed", encoding="utf-8")
    _write_provenance(paths, file_id="DOC-1", stored_relative_path="IMP-test/file.txt", digest="0" * 64)

    monkeypatch.setattr(helpers, "get_workspace_paths", lambda: paths)
    monkeypatch.setattr(
        helpers,
        "read_register_rows",
        lambda: [{"file_id": "DOC-1", "selected_for_export": "yes"}],
    )

    export_dir = paths.exports_dir / "export"
    export_dir.mkdir()
    with pytest.raises(ValueError, match="Integrity check failed"):
        helpers.copy_selected_files(export_dir)


def test_normal_selected_original_export(tmp_path, monkeypatch):
    paths = create_local_workspace(tmp_path / "repo")
    original = paths.originals_dir / "IMP-test" / "file.txt"
    original.parent.mkdir(parents=True)
    original.write_text("data", encoding="utf-8")
    _write_provenance(paths, file_id="DOC-1", stored_relative_path="IMP-test/file.txt", digest=sha256(original))

    monkeypatch.setattr(helpers, "get_workspace_paths", lambda: paths)
    monkeypatch.setattr(
        helpers,
        "read_register_rows",
        lambda: [{"file_id": "DOC-1", "selected_for_export": "yes"}],
    )

    export_dir = paths.exports_dir / "export"
    export_dir.mkdir()
    copied = helpers.copy_selected_files(export_dir)

    assert copied == ["selected_originals/file.txt"]
    assert (export_dir / "selected_originals/file.txt").read_text(encoding="utf-8") == "data"


def test_export_provenance_removes_absolute_source_path(tmp_path, monkeypatch):
    paths = create_local_workspace(tmp_path / "repo")
    original = paths.originals_dir / "IMP-test" / "file.txt"
    original.parent.mkdir(parents=True)
    original.write_text("data", encoding="utf-8")
    _write_provenance(
        paths,
        file_id="DOC-1",
        stored_relative_path="IMP-test/file.txt",
        digest=sha256(original),
        source_path="/home/private-user/very-private/file.txt",
    )

    monkeypatch.setattr(helpers, "get_workspace_paths", lambda: paths)

    export_dir = paths.exports_dir / "export"
    export_dir.mkdir()
    output = helpers.write_sanitized_provenance(export_dir)
    assert output is not None

    content = output.read_text(encoding="utf-8")
    assert "source_path" not in content
    assert "/home/private-user" not in content
    assert "sha256" in content
