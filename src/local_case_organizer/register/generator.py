from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths


@dataclass(frozen=True)
class RegisterRow:
    file_id: str
    sha256: str
    original_name: str
    relative_path: str
    suffix: str
    size_bytes: int
    imported_at_utc: str
    review_status: str
    note: str


def _sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_original_files(originals_dir: Path) -> list[Path]:
    return sorted([p for p in originals_dir.rglob("*") if p.is_file()])


def build_document_register() -> Path:
    create_local_workspace()
    paths = get_workspace_paths()
    files = _iter_original_files(paths.originals_dir)
    output_path = paths.register_dir / "document_register.csv"

    rows: list[RegisterRow] = []
    imported_at = datetime.now(UTC).isoformat()
    for index, file_path in enumerate(files, start=1):
        relative_path = file_path.relative_to(paths.originals_dir)
        rows.append(
            RegisterRow(
                file_id=f"DOC-{index:06d}",
                sha256=_sha256_for_file(file_path),
                original_name=file_path.name,
                relative_path=str(relative_path),
                suffix=file_path.suffix.lower(),
                size_bytes=file_path.stat().st_size,
                imported_at_utc=imported_at,
                review_status="unreviewed",
                note="",
            )
        )

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "file_id",
                "sha256",
                "original_name",
                "relative_path",
                "suffix",
                "size_bytes",
                "imported_at_utc",
                "review_status",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    return output_path
