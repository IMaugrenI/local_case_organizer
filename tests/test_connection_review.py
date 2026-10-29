"""A11: local organizational decisions never bypass source and case boundaries."""
from __future__ import annotations

from zipfile import ZipFile

import pytest

from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.audit import recent_changes
from local_case_organizer.document_text import index_document
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.ui.case_narrative import case_narrative
from local_case_organizer.ui.connection_review import (
    review_connection, reviewed_document_hints,
)
from local_case_organizer.ui.quick_intake import quick_organize_inbox


def _sources(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    for name, data in {
        "a.txt": "Aktenzeichen: 22 Ca 401/25\nA Text.\n",
        "b.txt": "Geschäftszeichen: 22 Ca 401/25\nB Text.\n",
        "private.txt": "Az.: 22 Ca 401/25\nPRIVATE-ONLY-FILE\n",
    }.items():
        (workspace.inbox_dir / name).write_text(data, encoding="utf-8")
    assert quick_organize_inbox()["imported_files"] == 3
    rows = read_register_rows()
    for row in rows:
        index_document(row["file_id"])
    return workspace, {row["original_name"]: row for row in rows}


def _review(decision="accepted_as_organizational_link"):
    groups = reviewed_document_hints()["groups"]
    assert len(groups) == 1
    group = groups[0]
    return review_connection(group["group_id"], group["source_signature"], decision)


def test_review_decisions_are_audited_idempotent_and_not_truth(tmp_path, monkeypatch):
    workspace, docs = _sources(tmp_path, monkeypatch)
    before = {p: (workspace.originals_dir / d["relative_path"]).read_bytes()
              for p, d in docs.items()}
    group = reviewed_document_hints()["groups"][0]
    assert group["status"] == "pending_review"
    saved = _review()
    assert saved["status"] == "accepted_as_organizational_link"
    assert reviewed_document_hints()["groups"][0]["status"] == "accepted_as_organizational_link"
    changes = [x for x in recent_changes() if x["area"] == "connections"]
    assert len(changes) == 1
    assert _review() == saved
    assert len([x for x in recent_changes() if x["area"] == "connections"]) == 1
    narrative = case_narrative()
    assert narrative["case_story_sections"][0]["review_status"] == "accepted_as_organizational_link"
    assert narrative["limits"]["identical_aktenzeichen_is_only_a_sorting_hint"]
    assert before == {p: (workspace.originals_dir / d["relative_path"]).read_bytes()
                      for p, d in docs.items()}
    _review("dismissed")
    assert reviewed_document_hints()["groups"][0]["status"] == "dismissed"


def test_changed_original_invalidates_review_and_rejects_stale_write(tmp_path, monkeypatch):
    workspace, docs = _sources(tmp_path, monkeypatch)
    group = reviewed_document_hints()["groups"][0]
    _review()
    original = workspace.originals_dir / docs["private.txt"]["relative_path"]
    original.write_text("Original geändert", encoding="utf-8")
    changed = reviewed_document_hints()
    assert changed["incomplete"]
    assert changed["groups"][0]["status"] == "recheck_required"
    with pytest.raises(ValueError, match="changed"):
        review_connection(group["group_id"], group["source_signature"], "dismissed")
    assert case_narrative()["case_story_sections"][0]["review_status"] == "recheck_required"


def test_new_group_member_requires_new_review(tmp_path, monkeypatch):
    workspace, docs = _sources(tmp_path, monkeypatch)
    old = reviewed_document_hints()["groups"][0]
    _review()
    (workspace.inbox_dir / "new.txt").write_text(
        "Aktenzeichen: 22 Ca 401/25\nNew evidence.\n", encoding="utf-8"
    )
    quick_organize_inbox()
    next_file = next(x for x in read_register_rows() if x["original_name"] == "new.txt")
    index_document(next_file["file_id"])
    updated = reviewed_document_hints()["groups"][0]
    assert updated["group_id"] == old["group_id"]
    assert updated["source_signature"] != old["source_signature"]
    assert updated["status"] == "recheck_required"
    with pytest.raises(ValueError, match="changed"):
        review_connection(old["group_id"], old["source_signature"], "dismissed")
    _review()
    assert reviewed_document_hints()["groups"][0]["status"] == "accepted_as_organizational_link"


def test_selected_only_handoff_never_reuses_full_case_review_or_private_source(tmp_path, monkeypatch):
    _workspace, docs = _sources(tmp_path, monkeypatch)
    _review()
    rows = read_register_rows()
    for row in rows:
        row["selected_for_export"] = "no" if row["original_name"] == "private.txt" else "yes"
    write_register_rows(rows)
    selected = {r["file_id"] for r in rows if r["selected_for_export"] == "yes"}
    selected_view = case_narrative(selected)
    assert selected_view["case_story_sections"][0]["review_status"] == "recheck_required"
    assert docs["private.txt"]["file_id"] not in str(selected_view)
    folder = build_export_package()
    with ZipFile(folder.with_suffix(".zip")) as archive:
        content = archive.read("SACHVERHALT_ARBEITSSTAND.md").decode()
        assert "recheck_required" in content
        assert "accepted_as_organizational_link" not in content
        assert "private.txt" not in content
        assert "PRIVATE-ONLY-FILE" not in content
        assert docs["private.txt"]["file_id"] not in content


def test_separate_case_cannot_inherit_legacy_review(tmp_path, monkeypatch):
    workspace, _docs = _sources(tmp_path, monkeypatch)
    _review()
    create_case(workspace.repo_root, "other")
    with using_case("other"):
        assert reviewed_document_hints()["groups"] == []
        with pytest.raises(ValueError, match="changed"):
            review_connection("0" * 24, "0" * 64, "dismissed")
    assert reviewed_document_hints()["groups"][0]["status"] == "accepted_as_organizational_link"


def test_review_inputs_and_ui_controls():
    with pytest.raises(ValueError, match="Invalid"):
        review_connection("../bad", "0" * 64, "dismissed")
    with pytest.raises(ValueError, match="Invalid"):
        review_connection("0" * 24, "0" * 64, "confirmed_truth")
    from local_case_organizer.ui.local_case_organizer_ui_narrative import NARRATIVE_SCRIPT
    assert "/api/review-connection" in NARRATIVE_SCRIPT
    assert "reviewConfirm" in NARRATIVE_SCRIPT
    assert "textContent" in NARRATIVE_SCRIPT
