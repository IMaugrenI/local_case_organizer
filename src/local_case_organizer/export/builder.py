from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths


EXPORT_FILES = [
    "document_register.csv",
    "timeline.csv",
    "provenance.csv",
]



def build_export_package() -> Path:
    create_local_workspace()
    paths = get_workspace_paths()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    export_dir = paths.exports_dir / f"case_export_{timestamp}"
    export_dir.mkdir(parents=True, exist_ok=True)

    included_files: list[str] = []
    for filename in EXPORT_FILES:
        source = paths.register_dir / filename
        if source.exists():
            shutil.copy2(source, export_dir / source.name)
            included_files.append(source.name)

    readme = export_dir / "README.txt"
    readme.write_text(
        "local_case_organizer export package\n"
        "=================================\n\n"
        "This export package is a neutral handoff bundle.\n"
        "It may contain a document register, a timeline, and provenance data.\n"
        "Legal review remains external to this repository.\n\n"
        f"Included files: {', '.join(included_files) if included_files else 'none'}\n",
        encoding="utf-8",
    )

    return export_dir
