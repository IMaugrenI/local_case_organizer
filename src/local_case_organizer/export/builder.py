from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.export.helpers import (
    build_zip_archive,
    copy_selected_files,
    write_export_manifest,
    write_sanitized_provenance,
    write_zip_checksum,
)
from local_case_organizer.paths import create_local_workspace, get_workspace_paths


EXPORT_FILES = [
    "document_register.csv",
    "timeline.csv",
    "claims.csv",
]


def build_export_package() -> Path:
    create_local_workspace()
    paths = get_workspace_paths()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    export_dir = paths.exports_dir / f"case_export_{timestamp}"
    export_dir.mkdir(parents=True, exist_ok=False)

    included_files: list[str] = []
    for filename in EXPORT_FILES:
        source = paths.register_dir / filename
        if source.exists():
            shutil.copy2(source, export_dir / source.name)
            included_files.append(source.name)

    sanitized_provenance = write_sanitized_provenance(export_dir)
    if sanitized_provenance is not None:
        included_files.append(sanitized_provenance.name)

    copied_selected = copy_selected_files(export_dir)

    readme = export_dir / "README.txt"
    readme.write_text(
        "local_case_organizer export package\n"
        "=================================\n\n"
        "This export package is a neutral handoff bundle.\n"
        "It may contain a document register, a timeline, sanitized provenance data, and selected original files.\n"
        "Absolute local source paths are intentionally excluded from the handoff provenance.\n"
        "Legal review remains external to this repository.\n\n"
        f"Included register files: {', '.join(included_files) if included_files else 'none'}\n"
        f"Selected original files: {len(copied_selected)}\n",
        encoding="utf-8",
    )

    zip_path = export_dir.with_suffix(".zip")
    write_export_manifest(export_dir, zip_path, included_files, copied_selected)
    zip_path = build_zip_archive(export_dir)
    write_zip_checksum(zip_path)

    return export_dir
