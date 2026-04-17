from __future__ import annotations

import csv
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths


REGISTER_FIELDS = [
    "file_id",
    "batch_id",
    "sha256",
    "original_name",
    "relative_path",
    "suffix",
    "size_bytes",
    "imported_at_utc",
    "review_status",
    "document_group",
    "selected_for_export",
    "note",
]

EDITABLE_REGISTER_FIELDS = [
    "review_status",
    "document_group",
    "selected_for_export",
    "note",
]


def register_path() -> Path:
    create_local_workspace()
    return get_workspace_paths().register_dir / "document_register.csv"


def read_register_rows() -> list[dict[str, str]]:
    path = register_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_register_rows(rows: list[dict[str, str]]) -> Path:
    path = register_path()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTER_FIELDS)
        writer.writeheader()
        for row in rows:
            normalized = {field: str(row.get(field, "")) for field in REGISTER_FIELDS}
            writer.writerow(normalized)
    return path
