"""A14: Review work items reuse audited tasks and never confer approval.

All input sources are synthetic isolated cases.
"""
from __future__ import annotations

import csv

import pytest

from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.claims import add_claim, read_claims, set_review_status
from local_case_organizer.document_text import index_document
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.tasks import (
    TASK_FIELDS, add_task, read_tasks, task_board, update_task,
)
from local_case_organizer.ui.connection_review import review_connection, reviewed_document_hints
from local_case_organizer.ui.quick_intake import quick_organize_inbox
from local_case_organizer.ui.review_workflow import (
    create_task_for_review, review_workflow,
)


def _case(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    home = paths.create_local_workspace()
    for name, body in {
        "alpha.txt": "Aktenzeichen: 44 Ca 123/26\nBetrag: 120 EUR\n",
        "beta.txt": "Geschäftszeichen: 44 Ca 123/26\nBetrag ungeprüft\n",
    }.items():
        (home.inbox_dir / name).write_text(body, encoding="utf-8")
    assert quick_organize_inbox()["imported_files"] == 2
    docs = {row["original_name"]: row for row in read_register_rows()}
    for row in read_register_rows():
        index_document(row["file_id"])
    return home, docs


def _candidate(kind, ref=None):
    items = [x for x in review_workflow()["candidates"] if x["kind"] == kind]
    assert items
    return next((x for x in items if x["ref"] == ref), items[0])


def _create(item):
    return create_task_for_review(item["kind"], item["ref"], item["token"])


def test_review_task_is_explicit_deduplicated_audited_and_never_approves(tmp_path, monkeypatch):
    home, docs = _case(tmp_path, monkeypatch)
    claim = add_claim(docs["alpha.txt"]["file_id"], 1, "Betrag: 120 EUR",
                      "Unbestätigte Aussage über die genannte Summe")
    item = _candidate("claim", claim["claim_id"])
    assert not read_tasks()
    first = _create(item)
    assert first["created"] is True
    again = _create(item)
    assert again["created"] is False
    assert first["task"]["task_id"] == again["task"]["task_id"]
    assert len(read_tasks()) == 1
    assert read_claims()[0]["review_status"] == "draft"
    assert home.originals_dir.joinpath(docs["alpha.txt"]["relative_path"]).is_file()
    records = home.register_dir / "change_audit.jsonl"
    assert '"area": "tasks"' in records.read_text(encoding="utf-8")

    workflow = review_workflow()
    assert workflow["review_tasks_total"] == 1
    assert workflow["review_tasks"][0]["source_status"] == "review_context_current"
    assert workflow["limitations"]["task_completion_never_approves_review_or_original"]
    update_task(first["task"]["task_id"], "done")
    assert read_claims()[0]["review_status"] == "draft"
    assert task_board()["tasks"][0]["date_indicator"] == "closed"
    assert _create(item)["created"] is True  # deliberately new after closing


def test_review_status_change_marks_context_drift_not_approval(tmp_path, monkeypatch):
    _home, docs = _case(tmp_path, monkeypatch)
    claim = add_claim(docs["alpha.txt"]["file_id"], 1, "Betrag: 120 EUR",
                      "Quellenprüfung offen")
    item = _candidate("claim", claim["claim_id"])
    task = _create(item)["task"]
    set_review_status(claim["claim_id"], "reviewed")
    result = review_workflow()
    linked = next(x for x in result["review_tasks"] if x["task_id"] == task["task_id"])
    assert linked["source_status"] == "review_item_not_in_current_queue"
    assert linked["task_status"] == "open"
    with pytest.raises(ValueError, match="changed"):
        _create(item)
    assert len(read_tasks()) == 1


def test_changed_connection_requires_operator_recheck(tmp_path, monkeypatch):
    _home, _docs = _case(tmp_path, monkeypatch)
    item = _candidate("connection")
    task = _create(item)["task"]
    link = reviewed_document_hints()["groups"][0]
    review_connection(link["group_id"], link["source_signature"],
                      "accepted_as_organizational_link")
    found = next(x for x in review_workflow()["review_tasks"]
                 if x["task_id"] == task["task_id"])
    assert found["source_status"] == "review_item_not_in_current_queue"
    assert found["task_status"] == "open"


def test_document_and_open_question_create_context_specific_tasks(tmp_path, monkeypatch):
    _home, _docs = _case(tmp_path, monkeypatch)
    document = _candidate("document")
    question = _candidate("question")
    saved_doc = _create(document)
    saved_question = _create(question)
    assert saved_doc["task"]["linked_file_ids"] == document["ref"]
    assert saved_question["task"]["linked_file_ids"] == ""
    assert saved_doc["task"]["review_kind"] == "document"
    assert saved_question["task"]["review_kind"] == "question"
    assert saved_question["task"]["due_date"] == ""


def test_legacy_task_csv_migrates_on_next_write_without_losing_rows(tmp_path, monkeypatch):
    home, docs = _case(tmp_path, monkeypatch)
    old_fields = TASK_FIELDS[:9]
    path = home.register_dir / "tasks.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=old_fields)
        writer.writeheader()
        writer.writerow({
            "task_id": "TSK-1234567890abcdef", "title": "Bestehende Aufgabe",
            "due_date": "", "status": "open", "priority": "normal",
            "linked_file_ids": docs["alpha.txt"]["file_id"],
            "note": "Handnotiz", "created_at_utc": "2026-01-01T00:00:00+00:00",
            "updated_at_utc": "2026-01-01T00:00:00+00:00",
        })
    assert read_tasks()[0]["title"] == "Bestehende Aufgabe"
    item = _candidate("document")
    _create(item)
    records = read_tasks()
    assert len(records) == 2
    assert records[0]["note"] == "Handnotiz"
    assert records[0]["review_kind"] == ""
    assert records[1]["review_kind"] == "document"
    assert list(csv.DictReader(path.open(encoding="utf-8", newline="")))[0]["title"] == "Bestehende Aufgabe"


def test_cross_case_tasks_are_isolated_and_bad_inputs_rejected(tmp_path, monkeypatch):
    home, _docs = _case(tmp_path, monkeypatch)
    item = _candidate("document")
    _create(item)
    create_case(home.repo_root, "second")
    with using_case("second"):
        assert review_workflow()["review_tasks_total"] == 0
        with pytest.raises(ValueError, match="changed"):
            _create(item)
        assert read_tasks() == []
    assert review_workflow()["review_tasks_total"] == 1
    with pytest.raises(ValueError, match="Invalid"):
        create_task_for_review("claim", "../escape", "0" * 64)
    with pytest.raises(ValueError, match="Invalid"):
        create_task_for_review("claim", "CLM-fake", "not-a-token")
    with pytest.raises(ValueError, match="changed"):
        create_task_for_review(item["kind"], item["ref"], "a" * 64)


def test_manual_task_and_ui_workflow_have_no_automatic_approval(tmp_path, monkeypatch):
    _home, _docs = _case(tmp_path, monkeypatch)
    normal = add_task("Unabhängige Aufgabe", note="Manual")
    assert normal["review_kind"] == ""
    from local_case_organizer.ui.local_case_organizer_ui_workflow import WORKFLOW_SCRIPT
    assert '"/api/create-review-task"' in WORKFLOW_SCRIPT
    assert '"/api/review-workflow"' in WORKFLOW_SCRIPT
    assert 'window.confirm(t("confirm"))' in WORKFLOW_SCRIPT
    assert 'box.addEventListener("toggle"' in WORKFLOW_SCRIPT
    assert "textContent" in WORKFLOW_SCRIPT
    assert '"/api/export-package"' not in WORKFLOW_SCRIPT
