from datetime import date

import pytest

from local_case_organizer import paths
from local_case_organizer.audit import recent_changes
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.register.store import write_register_rows
from local_case_organizer.tasks import add_task, task_board, update_task


def test_manual_date_indicators_and_audit(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    paths.create_local_workspace()
    write_register_rows([{"file_id": "DOC-1", "original_name": "test.txt"}])
    first = add_task("Review source", "2026-10-24", "high", "DOC-1")
    second = add_task("Contact witness", "2026-10-25", "normal")
    third = add_task("Write report", "2026-10-26", "low")
    statuses = [task["date_indicator"] for task in task_board(date(2026, 10, 25))["tasks"]]
    assert statuses == ["overdue", "due_today", "upcoming"]
    assert update_task(first["task_id"], "done")["status"] == "done"
    assert task_board(date(2026, 10, 25))["tasks"][-1]["date_indicator"] == "closed"
    assert [x["area"] for x in recent_changes()[:2]] == ["tasks", "tasks"]
    assert second["status"] == third["status"] == "open"


def test_unsafe_date_and_missing_refs_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    paths.create_local_workspace()
    with pytest.raises(ValueError, match="Due date"):
        add_task("Review source", "2026-02-30")
    with pytest.raises(ValueError, match="not in the selected case"):
        add_task("Review source", linked_file_ids="DOC-missing")


def test_case_isolation_and_manual_reopening(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    create_case(root, "alpha")
    create_case(root, "beta")
    with using_case("alpha"):
        task = add_task("Read the files")
        update_task(task["task_id"], "done")
        assert update_task(task["task_id"], "open")["status"] == "open"
    with using_case("beta"):
        assert task_board()["tasks"] == []
        with pytest.raises(ValueError, match="not found"):
            update_task(task["task_id"], "done")


def test_ui_exposes_task_board():
    from local_case_organizer.ui.app import HTML
    assert "task-board" in HTML and "/api/add-task" in HTML
