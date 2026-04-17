from __future__ import annotations

import shutil
from datetime import datetime, UTC
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths


def build_export_package() -> Path:
    create_local_workspace()
    paths = get_workspace_paths()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    export_dir = paths.exports_dir / f"case_export_{timestamp}"
    export_dir.mkdir(parents=True, exist_ok=True)

    register_file = paths.register_dir / "document_register.csv"
    timeline_file = paths.register_dir / "timeline.csv"

    if register_file.exists():
        shutil.copy2(register_file, export_dir / register_file.name)
    if timeline_file.exists():
        shutil.copy2(timeline_file, export_dir / timeline_file.name)

    readme = export_dir / "README.txt"
    readme.write_text(
        "local_case_organizer export package\n"
        "=================================\n\n"
        "This export package is a neutral handoff bundle.\n"
        "It may contain a document register and a timeline file.\n"
        "Legal review remains external to this repository.\n",
        encoding="utf-8",
    )

    return export_dir
