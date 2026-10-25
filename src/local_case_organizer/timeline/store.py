from __future__ import annotations

import csv

from local_case_organizer.audit import write_audited_csv
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths


TIMELINE_FIELDS = [
    "event_id",
    "event_date",
    "event_title",
    "linked_file_ids",
    "people_or_entities",
    "summary",
    "status",
]


def timeline_path() -> Path:
    create_local_workspace()
    return get_workspace_paths().register_dir / "timeline.csv"


def read_timeline_rows() -> list[dict[str, str]]:
    path = timeline_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_timeline_rows(rows: list[dict[str, str]]) -> Path:
    path = timeline_path()
    return write_audited_csv(path, TIMELINE_FIELDS, rows, "timeline")
