"""Explicit, bounded local intake: inbox -> existing provenance importer -> register.

No background worker, OCR, LLM, export, file removal, or auto-confirmation.
One click/drop is the processing gate. Repeated clicks skip unchanged bytes.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from threading import RLock

from local_case_organizer.imports.ingest import import_sources
from local_case_organizer.paths import create_local_workspace
from local_case_organizer.register.generator import build_document_register

_MAX_FILES = 64
_MAX_TOTAL_BYTES = 128 * 1024 * 1024
_LOCK = RLock()


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def quick_organize_inbox() -> dict[str, object]:
    """Import unseen inbox bytes only, then update the existing register.

    Files remain in the inbox so failed runs are recoverable. Registered copies
    remain under originals/ and are never deleted or rewritten by this action.
    A retry after partial success can safely rebuild the register.
    """
    with _LOCK:
        paths = create_local_workspace()
        inbox = paths.inbox_dir
        if inbox.is_symlink() or not inbox.is_dir():
            raise ValueError("Inbox is not a safe local folder")

        # No recursive symlinks, unbounded scans, or implicit processing of
        # arbitrary filesystem locations. The action is scoped to this case.
        candidates: list[Path] = []
        size = 0
        for entry in inbox.rglob("*"):
            if entry.is_symlink():
                raise ValueError("Inbox contains a symbolic link; review it manually")
            if not entry.is_file():
                continue
            candidates.append(entry)
            if len(candidates) > _MAX_FILES:
                raise ValueError("Too many inbox files; organize up to 64 at a time")
            size += entry.stat().st_size
            if size > _MAX_TOTAL_BYTES:
                raise ValueError("Inbox exceeds the 128 MiB quick-organize limit")
        candidates.sort()

        known_hashes: set[str] = set()
        provenance = paths.register_dir / "provenance.csv"
        if provenance.exists():
            if provenance.is_symlink() or provenance.stat().st_size > 8 * 1024 * 1024:
                raise ValueError("Provenance record is unsafe or too large")
            with provenance.open("r", encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    value = str(row.get("sha256", ""))
                    if len(value) == 64:
                        known_hashes.add(value)

        new_files: list[Path] = []
        skipped = 0
        for candidate in candidates:
            digest = _digest(candidate)
            if digest in known_hashes:
                skipped += 1
                continue
            known_hashes.add(digest)
            new_files.append(candidate)

        if new_files:
            import_sources(None, selected_files=new_files)

        # A previous attempt might have imported but not yet built the register.
        # Rebuild only if originals exist; preserve user-editable fields using
        # the existing generator's established merge behavior.
        if new_files or any(paths.originals_dir.iterdir()):
            build_document_register()

        return {
            "imported_files": len(new_files),
            "already_present": skipped,
            "pending_files": len(candidates),
            "register_ready": bool(new_files or paths.register_dir.joinpath("document_register.csv").exists()),
        }
