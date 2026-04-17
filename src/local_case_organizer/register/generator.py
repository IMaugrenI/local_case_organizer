from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths


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



def build_document_register() -> Path:
    create_local_workspace()
    paths = get_workspace_paths()
    files = _iter_original_files(paths.originals_dir)
    output_path = paths.register_dir / "document_register.csv"
    provenance_index = _load_provenance_index(paths.register_dir)

    rows: list[RegisterRow] = []
    generated_at = datetime.now(UTC).isoformat()
    for index, file_path in enumerate(files, start=1):
        relative_path = str(file_path.relative_to(paths.originals_dir))
        file_hash = _sha256_for_file(file_path)
        provenance = provenance_index.get(relative_path)

        file_id = provenance["file_id"] if provenance and provenance.get("sha256") == file_hash else f"UNTRACKED-{index:06d}"
        batch_id = provenance["batch_id"] if provenance and provenance.get("sha256") == file_hash else ""
        imported_at = provenance["imported_at_utc"] if provenance and provenance.get("sha256") == file_hash else generated_at

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
                review_status="unreviewed",
                document_group="",
                selected_for_export="no",
                note="",
            )
        )

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
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
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    return output_path
