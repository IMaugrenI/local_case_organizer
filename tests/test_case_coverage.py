"""A13 synthetic-only coverage checks, never operator acceptance."""
from __future__ import annotations

from pathlib import Path

from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.document_text import index_document
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.tasks import add_task
from local_case_organizer.ui.case_coverage import case_coverage
from local_case_organizer.ui.quick_intake import quick_organize_inbox


def _case(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    paths_out = paths.create_local_workspace()
    for name, body in {
        "indexed.txt": "Synthetic data about a document.\n",
        "unindexed.txt": "Another synthetic document.\n",
        "empty.txt": "",
        "modified.txt": "Initially imported.\n",
        "removed.txt": "About to disappear.\n",
    }.items():
        (paths_out.inbox_dir / name).write_text(body, encoding="utf-8")
    assert quick_organize_inbox()["imported_files"] == 5
    docs = {r["original_name"]: r for r in read_register_rows()}
    index_document(docs["indexed.txt"]["file_id"])
    index_document(docs["empty.txt"]["file_id"])
    return paths_out, docs


def _states(report):
    return {row["original_name"]: row["status"] for row in report["source_samples"]}


def test_source_coverage_distinguishes_hash_index_and_missing_original(tmp_path, monkeypatch):
    workspace, docs = _case(tmp_path, monkeypatch)
    (workspace.originals_dir / docs["modified.txt"]["relative_path"]).write_text(
        "Original edited after import.", encoding="utf-8"
    )
    (workspace.originals_dir / docs["removed.txt"]["relative_path"]).unlink()
    result = case_coverage()
    assert result["total_registered"] == 5
    assert result["not_scanned"] == 0
    assert _states(result) == {
        "indexed.txt": "source_text_available",
        "unindexed.txt": "index_needed",
        "empty.txt": "index_has_no_text",
        "modified.txt": "original_changed",
        "removed.txt": "original_missing",
    }
    assert result["counts"]["source_text_available"] == 1
    assert result["incomplete"] is True
    assert result["limitations"]["does_not_prove_real_world_file_completeness"]
    assert not (workspace.register_dir / "integrity_journal.jsonl").exists()


def test_manual_unlinked_items_and_stale_references_are_only_organizational(tmp_path, monkeypatch):
    _workspace, _docs = _case(tmp_path, monkeypatch)
    add_task("Check a source document", note="No legal deadline entered")
    result = case_coverage()
    assert result["manual_links"]["areas"]["tasks"]["without_document_link"] == 1
    assert result["manual_links"]["areas"]["tasks"]["with_unknown_document_link"] == 0
    assert result["manual_links"]["unknown_document_ids"] == []
    assert result["limitations"]["does_not_establish_truth_or_legal_findings"]


def test_source_coverage_is_bounded_and_case_private(tmp_path, monkeypatch):
    workspace, _docs = _case(tmp_path, monkeypatch)
    import local_case_organizer.ui.case_coverage as coverage
    monkeypatch.setattr(coverage, "MAX_SCANNED", 2)
    result = coverage.case_coverage()
    assert result["total_registered"] == 5
    assert result["scanned"] == 2
    assert result["not_scanned"] == 3
    assert result["incomplete"] is True
    create_case(workspace.repo_root, "another")
    with using_case("another"):
        other = coverage.case_coverage()
        assert other["total_registered"] == 0
        assert other["source_samples"] == []
        assert other["manual_links"]["areas"]["timeline"]["entries"] == 0
    assert coverage.case_coverage()["total_registered"] == 5


def test_inconsistent_provenance_not_credited_as_verified(tmp_path, monkeypatch):
    _workspace, docs = _case(tmp_path, monkeypatch)
    rows = read_register_rows()
    for row in rows:
        if row["file_id"] == docs["indexed.txt"]["file_id"]:
            row["sha256"] = "f" * 64
    write_register_rows(rows)
    result = case_coverage()
    assert _states(result)["indexed.txt"] == "provenance_unavailable"
    assert result["counts"].get("source_text_available", 0) == 0


def test_coverage_view_uses_existing_runtime_without_implicit_actions():
    from local_case_organizer.ui.local_case_organizer_ui_coverage import COVERAGE_SCRIPT
    assert '"/api/case-coverage"' in COVERAGE_SCRIPT
    assert 'id="lco-coverage"' not in COVERAGE_SCRIPT  # initialized through DOM only
    assert "box.addEventListener(\"toggle\"" in COVERAGE_SCRIPT
    assert "if(box.open)refresh()" in COVERAGE_SCRIPT
    assert "textContent" in COVERAGE_SCRIPT
    assert '"/api/export-package"' not in COVERAGE_SCRIPT
    override = (Path(__file__).resolve().parents[1] / "src" / "local_case_organizer"
                / "ui" / "local_case_organizer_ui_override.py").read_text(encoding="utf-8")
    assert "COVERAGE_SCRIPT" in override and "COVERAGE_CSS" in override
