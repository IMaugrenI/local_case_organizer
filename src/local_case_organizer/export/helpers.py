from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.register.store import read_register_rows



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
            continue
        stored_relative_path = provenance.get("stored_relative_path", "")
        if not stored_relative_path:
            continue
        source = paths.originals_dir / stored_relative_path
        if not source.exists() or not source.is_file():
            continue
        target = selected_dir / Path(stored_relative_path).name
        if target.exists():
            target = target.with_name(f"{target.stem}_{file_id}{target.suffix}")
        shutil.copy2(source, target)
        copied.append(str(target.relative_to(export_dir)))
    return copied



def build_zip_archive(export_dir: Path) -> Path:
    zip_path = export_dir.with_suffix(".zip")
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in export_dir.rglob("*"):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(export_dir))
    return zip_path



def write_export_manifest(export_dir: Path, zip_path: Path, included_files: list[str], copied_selected: list[str]) -> Path:
    manifest = export_dir / "export_manifest.json"
    payload = {
        "export_dir": export_dir.name,
        "zip_name": zip_path.name,
        "included_register_files": included_files,
        "selected_originals_count": len(copied_selected),
        "selected_original_files": copied_selected,
    }
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest
