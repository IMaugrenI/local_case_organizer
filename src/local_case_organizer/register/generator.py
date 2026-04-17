from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths
from local_case_organizer.register.store import EDITABLE_REGISTER_FIELDS, REGISTER_FIELDS, read_register_rows


@dataclass(frozen=True)
class RegisterRow:
    file_id: str
    batch_id: str
    sha256: str
    original_name: str
    relative_path: str
    suffix: str
    size_bytes: int
    imported_at_utc: str
    review_status: str
    document_group: str
    selected_for_export: str
    note: str


PROVENANCE_FIELDS = [
    "batch_id",
    "file_id",
    "imported_at_utc",
    "source_label",
    "source_path",
    "original_name",
    "stored_relative_path",
    "sha256",
    "size_bytes",
]



def _sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()



def _iter_original_files(originals_dir: Path) -> list[Path]:
    return sorted([path for path in originals_dir.rglob("*") if path.is_file()])



def _load_provenance_index(register_dir: Path) -> dict[str, dict[str, str]]:
    provenance_path = register_dir / "provenance.csv"
    if not provenance_path.exists():
        return {}

    index: dict[str, dict[str, str]] = {}
    with provenance_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            stored_relative_path = row.get("stored_relative_path", "")
            if stored_relative_path:
                index[stored_relative_path] = row
    return index



def _load_existing_register_index() -> dict[str, dict[str, str]]:
    rows = read_register_rows()
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get("file_id") or row.get("relative_path")
        if key:
            index[key] = row
    return index



def build_document_register() -> Path:
    create_local_workspace()
    paths = get_workspace_paths()
    files = _iter_original_files(paths.originals_dir)
    output_path = paths.register_dir / "document_register.csv"
    provenance_index = _load_provenance_index(paths.register_dir)
    existing_index = _load_existing_register_index()

    rows: list[RegisterRow] = []
    generated_at = datetime.now(UTC).isoformat()
    for index, file_path in enumerate(files, start=1):
        relative_path = str(file_path.relative_to(paths.originals_dir))
        file_hash = _sha256_for_file(file_path)
        provenance = provenance_index.get(relative_path)

        file_id = provenance["file_id"] if provenance and provenance.get("sha256") == file_hash else f"UNTRACKED-{index:06d}"
        batch_id = provenance["batch_id"] if provenance and provenance.get("sha256") == file_hash else ""
        imported_at = provenance["imported_at_utc"] if provenance and provenance.get("sha256") == file_hash else generated_at

        existing = existing_index.get(file_id) or existing_index.get(relative_path) or {}
        editable = {field: existing.get(field, "") for field in EDITABLE_REGISTER_FIELDS}

        rows.append(
            RegisterRow(
                file_id=file_id,
                batch_id=batch_id,
                sha256=file_hash,
                original_name=file_path.name,
                relative_path=relative_path,
                suffix=file_path.suffix.lower(),
                size_bytes=file_path.stat().st_size,
                imported_at_utc=imported_at,
                review_status=editable.get("review_status") or "unreviewed",
                document_group=editable.get("document_group") or "",
                selected_for_export=editable.get("selected_for_export") or "no",
                note=editable.get("note") or "",
            )
        )

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTER_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    return output_path
