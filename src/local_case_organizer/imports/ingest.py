from __future__ import annotations

import csv
import hashlib
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.paths import WorkspacePaths, create_local_workspace, get_workspace_paths


MANIFEST_PREFIX = "import_manifest_"
MANIFEST_FIELDS = [
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


@dataclass(frozen=True)
class ImportRow:
    batch_id: str
    file_id: str
    imported_at_utc: str
    source_label: str
    source_path: str
    original_name: str
    stored_relative_path: str
    sha256: str
    size_bytes: int


def _sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()



def _iter_source_files(source_path: Path) -> list[Path]:
    if source_path.is_file():
        return [source_path]
    return sorted([path for path in source_path.rglob("*") if path.is_file()])



def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1



def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str | int]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)



def rebuild_provenance_table(paths: WorkspacePaths | None = None) -> Path:
    workspace_paths = paths or get_workspace_paths()
    manifests = sorted(workspace_paths.register_dir.glob(f"{MANIFEST_PREFIX}*.csv"))
    output_path = workspace_paths.register_dir / "provenance.csv"
    rows: list[dict[str, str | int]] = []

    for manifest in manifests:
        with manifest.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows.extend(reader)

    _write_csv(output_path, MANIFEST_FIELDS, rows)
    return output_path



def import_sources(source: str | None = None) -> dict[str, object]:
    paths = create_local_workspace()
    source_path = Path(source).expanduser().resolve() if source else paths.inbox_dir.resolve()
    source_label = "cli-source" if source else "local-inbox"

    if not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    files = _iter_source_files(source_path)
    if not files:
        raise ValueError(f"No files found to import: {source_path}")

    imported_at = datetime.now(UTC)
    batch_timestamp = imported_at.strftime("%Y%m%dT%H%M%SZ")
    batch_id = f"IMP-{batch_timestamp}"
    batch_root = paths.originals_dir / batch_id
    batch_root.mkdir(parents=True, exist_ok=True)

    rows: list[ImportRow] = []
    for index, file_path in enumerate(files, start=1):
        relative_part = file_path.relative_to(source_path) if source_path.is_dir() else Path(file_path.name)
        destination = _next_available_path(batch_root / relative_part)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, destination)

        file_id = f"DOC-{batch_timestamp}-{index:04d}"
        rows.append(
            ImportRow(
                batch_id=batch_id,
                file_id=file_id,
                imported_at_utc=imported_at.isoformat(),
                source_label=source_label,
                source_path=str(file_path),
                original_name=file_path.name,
                stored_relative_path=str(destination.relative_to(paths.originals_dir)),
                sha256=_sha256_for_file(destination),
                size_bytes=destination.stat().st_size,
            )
        )

    manifest_path = paths.register_dir / f"{MANIFEST_PREFIX}{batch_id}.csv"
    _write_csv(manifest_path, MANIFEST_FIELDS, [asdict(row) for row in rows])
    provenance_path = rebuild_provenance_table(paths)

    return {
        "batch_id": batch_id,
        "source": str(source_path),
        "source_label": source_label,
        "imported_files": len(rows),
        "batch_root": str(batch_root),
        "manifest_path": str(manifest_path),
        "provenance_path": str(provenance_path),
    }
