"""Manually managed reminders and tasks scoped to the existing local case.

Dates are entered by the operator: no legal deadline calculation or
automatic notification. The only status derived from a date is whether a
user-entered date is earlier than, equal to, or later than the local day.
"""
from __future__ import annotations

import re
from datetime import UTC, date, datetime
from threading import RLock
from uuid import uuid4

from local_case_organizer.audit import write_audited_csv
from local_case_organizer.paths import create_local_workspace, get_workspace_paths
from local_case_organizer.register.store import read_register_rows

TASK_FIELDS = [
    "task_id", "title", "due_date", "status", "priority", "linked_file_ids",
    "note", "created_at_utc", "updated_at_utc",
]
STATUSES = {"open", "in_progress", "done", "cancelled"}
PRIORITIES = {"low", "normal", "high"}
MAX_TASKS = 1200
_LOCK = RLock()


def _path():
    return get_workspace_paths().register_dir / "tasks.csv"


def _due(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Due date must be YYYY-MM-DD or empty")
    if not value:
        return ""
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Due date must be YYYY-MM-DD or empty") from exc
    if parsed.isoformat() != value:
        raise ValueError("Due date must be canonical YYYY-MM-DD")
    return value


def _links(value: str) -> str:
    if not isinstance(value, str) or len(value) > 800:
        raise ValueError("Invalid document references")
    references = list(dict.fromkeys(item.strip() for item in value.split(",") if item.strip()))
    if len(references) > 20 or any(not re.fullmatch(r"[a-zA-Z0-9_-]{1,110}", r) for r in references):
        raise ValueError("Too many or invalid document references")
    known = {str(row.get("file_id", "")).strip() for row in read_register_rows()}
    if any(ref not in known for ref in references):
        raise ValueError("A referenced file ID is not in the selected case")
    return ",".join(references)


def read_tasks() -> list[dict[str, str]]:
    path = _path()
    if not path.exists():
        return []
    if path.is_symlink() or path.stat().st_size > 1024 * 1024:
        raise ValueError("Task table is unsafe or too large")
    import csv
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) > MAX_TASKS:
        raise ValueError("Task limit exceeded")
    return rows


def _save(rows):
    create_local_workspace()
    write_audited_csv(_path(), TASK_FIELDS, rows, "tasks")


def add_task(title: str, due_date: str = "", priority: str = "normal",
             linked_file_ids: str = "", note: str = "") -> dict:
    if not isinstance(title, str) or not 3 <= len(title.strip()) <= 180:
        raise ValueError("Task title must have 3–180 characters")
    if priority not in PRIORITIES:
        raise ValueError("Invalid task priority")
    if not isinstance(note, str) or len(note) > 1200:
        raise ValueError("Task note is too long")
    due_date = _due(due_date)
    references = _links(linked_file_ids)
    now = datetime.now(UTC).isoformat()
    with _LOCK:
        existing = read_tasks()
        if len(existing) >= MAX_TASKS:
            raise ValueError("Task limit reached")
        task = {
            "task_id": "TSK-" + uuid4().hex[:16],
            "title": title.strip(), "due_date": due_date, "status": "open",
            "priority": priority, "linked_file_ids": references, "note": note,
            "created_at_utc": now, "updated_at_utc": now,
        }
        _save([*existing, task])
        return task


def update_task(task_id: str, status: str) -> dict:
    if not isinstance(task_id, str) or not re.fullmatch(r"TSK-[a-f0-9]{16}", task_id):
        raise ValueError("Invalid task ID")
    if status not in STATUSES:
        raise ValueError("Invalid task status")
    with _LOCK:
        records = read_tasks()
        task = next((row for row in records if row.get("task_id") == task_id), None)
        if task is None:
            raise ValueError("Task not found")
        if task["status"] != status:
            task["status"] = status
            task["updated_at_utc"] = datetime.now(UTC).isoformat()
            _save(records)
        return dict(task)


def task_board(as_of: date | None = None) -> dict:
    today = as_of or date.today()
    tasks = []
    for task in read_tasks():
        entry = dict(task)
        if entry.get("status") in {"done", "cancelled"}:
            marker = "closed"
        elif not entry.get("due_date"):
            marker = "unscheduled"
        else:
            try:
                due = date.fromisoformat(str(entry["due_date"]))
                marker = "overdue" if due < today else "due_today" if due == today else "upcoming"
            except ValueError:
                marker = "invalid_manual_date"
        entry["date_indicator"] = marker
        tasks.append(entry)
    rank = {"overdue":0, "due_today":1, "upcoming":2,
            "unscheduled":3, "invalid_manual_date":4, "closed":5}
    tasks.sort(key=lambda task: (rank.get(task["date_indicator"], 10),
                                 str(task.get("due_date", "")),
                                 str(task.get("created_at_utc", ""))))
    return {"as_of": today.isoformat(), "tasks": tasks,
            "note": ("Dates are entered manually. Indicators are organizational only, "
                     "not legally calculated deadlines or external notifications.")}
