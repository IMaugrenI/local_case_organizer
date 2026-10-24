from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.register.store import read_register_rows


SAFE_PROVENANCE_FIELDS = [
    "batch_id",
    "file_id",
    "imported_at_utc",
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


def _within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def load_provenance_index(register_dir: Path) -> dict[str, dict[str, str]]:
    provenance_path = register_dir / "provenance.csv"
    if not provenance_path.exists():
        return {}

    index: dict[str, dict[str, str]] = {}
    with provenance_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            file_id = row.get("file_id", "")
            if file_id:
                index[file_id] = row
    return index


def _resolve_original_path(originals_dir: Path, stored_relative_path: str) -> Path:
    raw = Path(stored_relative_path)
    if raw.is_absolute():
        raise ValueError("Stored original path must be relative")

    base = originals_dir.resolve()
    candidate = (base / raw).resolve()
    if not _within(base, candidate):
        raise ValueError("Stored original path escapes originals directory")
    if not candidate.exists() or not candidate.is_file():
        raise FileNotFoundError(f"Stored original is missing: {stored_relative_path}")
    return candidate


def copy_selected_files(export_dir: Path) -> list[str]:
    paths = get_workspace_paths()
    rows = read_register_rows()
    provenance_index = load_provenance_index(paths.register_dir)
    selected_dir = export_dir / "selected_originals"
    selected_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for row in rows:
        if str(row.get("selected_for_export", "")).lower() != "yes":
            continue

        file_id = str(row.get("file_id", ""))
        provenance = provenance_index.get(file_id)
        if not provenance:
            raise ValueError(f"Missing provenance for selected file: {file_id}")

        stored_relative_path = provenance.get("stored_relative_path", "")
        expected_sha256 = provenance.get("sha256", "")
        if not stored_relative_path or not expected_sha256:
            raise ValueError(f"Incomplete provenance for selected file: {file_id}")

        source = _resolve_original_path(paths.originals_dir, stored_relative_path)
        actual_sha256 = _sha256_for_file(source)
        if actual_sha256 != expected_sha256:
            raise ValueError(f"Integrity check failed for selected file: {file_id}")

        target = selected_dir / Path(stored_relative_path).name
        if target.exists():
            target = target.with_name(f"{target.stem}_{file_id}{target.suffix}")
        shutil.copy2(source, target)
        copied.append(str(target.relative_to(export_dir)))

    return copied


def write_sanitized_provenance(export_dir: Path) -> Path | None:
    paths = get_workspace_paths()
    source_path = paths.register_dir / "provenance.csv"
    if not source_path.exists():
        return None

    output_path = export_dir / "provenance.csv"
    with source_path.open("r", encoding="utf-8", newline="") as source_handle:
        reader = csv.DictReader(source_handle)
        rows = [{field: row.get(field, "") for field in SAFE_PROVENANCE_FIELDS} for row in reader]

    with output_path.open("w", encoding="utf-8", newline="") as output_handle:
        writer = csv.DictWriter(output_handle, fieldnames=SAFE_PROVENANCE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def build_zip_archive(export_dir: Path) -> Path:
    zip_path = export_dir.with_suffix(".zip")
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(export_dir.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(export_dir))
    return zip_path


def write_export_manifest(
    export_dir: Path,
    zip_path: Path,
    included_files: list[str],
    copied_selected: list[str],
) -> Path:
    manifest = export_dir / "export_manifest.json"
    file_hashes: dict[str, str] = {}
    for path in sorted(export_dir.rglob("*")):
        if path.is_file() and path != manifest:
            file_hashes[str(path.relative_to(export_dir))] = _sha256_for_file(path)

    payload = {
        "export_dir": export_dir.name,
        "zip_name": zip_path.name,
        "included_register_files": included_files,
        "selected_originals_count": len(copied_selected),
        "selected_original_files": copied_selected,
        "files_sha256": file_hashes,
    }
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest


def write_zip_checksum(zip_path: Path) -> Path:
    checksum_path = zip_path.with_suffix(zip_path.suffix + ".sha256")
    checksum_path.write_text(f"{_sha256_for_file(zip_path)}  {zip_path.name}\n", encoding="utf-8")
    return checksum_path
