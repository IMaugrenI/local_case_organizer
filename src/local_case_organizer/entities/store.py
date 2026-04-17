from __future__ import annotations

import csv
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
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENTITY_FIELDS)
        writer.writeheader()
        for row in rows:
            normalized = {field: str(row.get(field, "")) for field in ENTITY_FIELDS}
            writer.writerow(normalized)
    return path
