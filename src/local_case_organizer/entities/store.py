from __future__ import annotations

import csv

from local_case_organizer.audit import write_audited_csv
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths


ENTITY_FIELDS = [
    "entity_id",
    "entity_name",
    "entity_type",
    "linked_file_ids",
    "notes",
]


def entities_path() -> Path:
    create_local_workspace()
    return get_workspace_paths().register_dir / "entities.csv"


def read_entity_rows() -> list[dict[str, str]]:
    path = entities_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_entity_rows(rows: list[dict[str, str]]) -> Path:
    path = entities_path()
    return write_audited_csv(path, ENTITY_FIELDS, rows, "entities")
