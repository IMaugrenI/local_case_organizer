"""Guided intake contracts: bounded, idempotent and no destructive side effects."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from local_case_organizer.ui import quick_intake
from local_case_organizer.ui.local_case_organizer_ui_simple import SIMPLE_CSS, SIMPLE_SCRIPT


def workspace(tmp_path, monkeypatch):
    paths = SimpleNamespace(
        inbox_dir=tmp_path / "data" / "inbox",
        register_dir=tmp_path / "data" / "register",
        originals_dir=tmp_path / "data" / "originals",
    )
    for path in vars(paths).values():
        path.mkdir(parents=True)
    monkeypatch.setattr(quick_intake, "create_local_workspace", lambda: paths)
    return paths


def test_quick_intake_deduplicates_and_preserves_inbox(tmp_path, monkeypatch):
    paths = workspace(tmp_path, monkeypatch)
    (paths.inbox_dir / "letter.pdf").write_bytes(b"%PDF-FAKE-TEST")
    (paths.inbox_dir / "same-content.pdf").write_bytes(b"%PDF-FAKE-TEST")
    imported = []
    def import_batch(source, *, selected_files):
        assert source is None
        imported.extend(file.name for file in selected_files)
        checksum = hashlib.sha256(selected_files[0].read_bytes()).hexdigest()
        with (paths.register_dir / "provenance.csv").open("w", newline="", encoding="utf-8") as stream:
            out = csv.DictWriter(stream, fieldnames=["sha256"])
            out.writeheader()
            out.writerow({"sha256": checksum})
        (paths.originals_dir / "batch").mkdir(exist_ok=True)
        return {"imported_files": len(selected_files)}
    builds = []
    def build():
        builds.append(True)
        (paths.register_dir / "document_register.csv").write_text("id\n", encoding="utf-8")
    monkeypatch.setattr(quick_intake, "import_sources", import_batch)
    monkeypatch.setattr(quick_intake, "build_document_register", build)
    first = quick_intake.quick_organize_inbox()
    assert first["imported_files"] == 1
    assert first["already_present"] == 1
    assert imported == ["letter.pdf"]
    second = quick_intake.quick_organize_inbox()
    assert second["imported_files"] == 0
    assert second["already_present"] == 2
    assert imported == ["letter.pdf"]
    assert len(builds) == 2
    assert (paths.inbox_dir / "letter.pdf").read_bytes() == b"%PDF-FAKE-TEST"


def test_quick_intake_refuses_symlinks_and_oversized_batches(tmp_path, monkeypatch):
    paths = workspace(tmp_path, monkeypatch)
    target = tmp_path / "outside.txt"
    target.write_text("secret", encoding="utf-8")
    (paths.inbox_dir / "shortcut").symlink_to(target)
    monkeypatch.setattr(quick_intake, "import_sources", lambda *a, **k: pytest.fail("called"))
    with pytest.raises(ValueError, match="symbolic link"):
        quick_intake.quick_organize_inbox()
    (paths.inbox_dir / "shortcut").unlink()
    for index in range(65):
        (paths.inbox_dir / ("doc-%03d.txt" % index)).write_text("one-%d" % index, encoding="utf-8")
    # A large inbox is processed in safe batches, not blocked forever.
    monkeypatch.setattr(quick_intake, "import_sources", lambda source, *, selected_files: None)
    monkeypatch.setattr(quick_intake, "build_document_register", lambda: None)
    result = quick_intake.quick_organize_inbox()
    assert result["imported_files"] == 64
    assert result["remaining_files"] == 1

    with pytest.raises(ValueError, match="Invalid inbox filename"):
        quick_intake.quick_organize_inbox(["../outside.txt"])
    with pytest.raises(ValueError, match="missing or unsafe"):
        quick_intake.quick_organize_inbox(["does-not-exist.pdf"])




def test_real_intake_preserves_existing_register_edits(tmp_path, monkeypatch):
    """Exercise the actual importer and audited register on an isolated case."""
    from local_case_organizer import paths as paths_module
    from local_case_organizer.register.store import read_register_rows, write_register_rows

    monkeypatch.setattr(paths_module, "get_repo_root", lambda: tmp_path)
    paths = paths_module.create_local_workspace()
    first_source = paths.inbox_dir / "first.pdf"
    first_source.write_bytes(b"%PDF-1.4 test original")
    initial = quick_intake.quick_organize_inbox()
    assert initial["imported_files"] == 1
    rows = read_register_rows()
    assert len(rows) == 1
    assert rows[0]["file_id"].startswith("DOC-")
    registered_copy = paths.originals_dir / rows[0]["relative_path"]
    assert registered_copy.read_bytes() == first_source.read_bytes()
    rows[0]["note"] = "Keep this manual note"
    write_register_rows(rows)

    another = paths.inbox_dir / "second.txt"
    another.write_text("Another document", encoding="utf-8")
    second = quick_intake.quick_organize_inbox()
    assert second["imported_files"] == 1
    assert second["already_present"] == 1
    after = read_register_rows()
    assert len(after) == 2
    original = next(row for row in after if row["original_name"] == "first.pdf")
    assert original["note"] == "Keep this manual note"
    assert original["file_id"] == rows[0]["file_id"]
    assert registered_copy.read_bytes() == first_source.read_bytes()
    assert first_source.exists() and another.exists()
    retry = quick_intake.quick_organize_inbox()
    assert retry["imported_files"] == 0
    assert len(read_register_rows()) == 2

def test_simple_mode_is_opt_in_for_processing_and_expert_view_remains():
    assert "lco-simple-mode" in SIMPLE_CSS
    assert "lco-simple-drop" in SIMPLE_SCRIPT
    assert '"/api/upload"' in SIMPLE_SCRIPT
    assert '"/api/quick-organize"' in SIMPLE_SCRIPT
    assert "organize(saved.uploaded_files)" in SIMPLE_SCRIPT
    assert "event.preventDefault()" in SIMPLE_SCRIPT
    assert '"advanced"' in SIMPLE_SCRIPT
    assert 'openView("export")' in SIMPLE_SCRIPT
    assert "requestAnimationFrame" not in SIMPLE_SCRIPT
    assert "import-ai-review" not in SIMPLE_SCRIPT
    assert "export-package" not in SIMPLE_SCRIPT


def test_existing_entrypoint_injects_simple_view_with_advanced_ui():
    script = """
import run
import local_case_organizer.ui.app as ui
html = ui.run_ui.__globals__["HTML"]
assert "lco-easy-home" in html
assert 'lco-simple-drop' in html
assert 'lco-workspace-nav' in html
assert 'api/quick-organize' in html
assert 'lco-top-toggles' in html
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stderr
