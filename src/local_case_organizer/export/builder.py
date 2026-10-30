from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import shutil

from local_case_organizer.export.helpers import (
    build_zip_archive,
    copy_selected_files,
    write_export_manifest,
    write_sanitized_provenance,
    write_zip_checksum,
)
from local_case_organizer.export.dossier import write_dossier
from local_case_organizer.export.quality import handoff_quality
from local_case_organizer.export.quality_report import write_quality_report
from local_case_organizer.export.handoff import write_lawyer_start_here
from local_case_organizer.ui.case_narrative import write_case_narrative
from local_case_organizer.paths import create_local_workspace, get_workspace_paths
from local_case_organizer.register.store import read_register_rows


EXPORT_FILES = [
    "document_register.csv",
    "timeline.csv",
    "claims.csv",
]


def build_export_package() -> Path:
    create_local_workspace()
    # A fresh selected-only preview checks sources before creating an export.
    quality = handoff_quality()
    if quality["export_blocked_in_scanned_sources"]:
        raise ValueError("Integrity preflight failed for selected originals; review the handoff preview")
    paths = get_workspace_paths()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    export_dir = paths.exports_dir / f"case_export_{timestamp}"
    export_dir.mkdir(parents=True, exist_ok=False)

    try:
        # Only records linked to explicitly selected originals leave the case.
        # This prevents an otherwise innocuous handoff from exposing the names,
        # notes or event descriptions of unrelated private files.
        from local_case_organizer.export.handoff import write_selected_tables
        selected_ids = {str(row.get("file_id", "")) for row in read_register_rows()
                        if str(row.get("selected_for_export", "")).lower() == "yes"}
        included_files = write_selected_tables(export_dir, selected_ids)

        sanitized_provenance = write_sanitized_provenance(export_dir)
        if sanitized_provenance is not None:
            included_files.append(sanitized_provenance.name)

        copied_selected = copy_selected_files(export_dir)
        write_dossier(export_dir, copied_selected)
        write_lawyer_start_here(export_dir, selected_ids)
        write_case_narrative(export_dir, selected_ids)
        write_quality_report(export_dir, quality)

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
    except Exception:
        # This directory was just created for this export. Do not retain a
        # partially prepared or partially zipped private handoff after error.
        shutil.rmtree(export_dir)
        for artifact in (export_dir.with_suffix(".zip"),
                         export_dir.with_suffix(".zip.sha256")):
            artifact.unlink(missing_ok=True)
        raise
