from __future__ import annotations

import csv

from local_case_organizer.audit import write_audited_csv
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
    return write_audited_csv(path, REGISTER_FIELDS, rows, "register")
