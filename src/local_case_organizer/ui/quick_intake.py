"""Explicit, bounded local intake using the existing import/register pipeline.

No background worker, OCR, LLM, export, deletion, or automatic approval.
The user's file drop or button click is the processing gate.
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
_MAX_SCANNED = 4096
_LOCK = RLock()


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _requested_files(inbox: Path, names: list[str]) -> list[Path]:
    if not isinstance(names, list) or len(names) > _MAX_FILES:
        raise ValueError("Invalid file selection or too many files")
    candidates = []
    for name in names:
        if (not isinstance(name, str) or not name or len(name) > 240
                or name in {".", ".."} or "/" in name or "\\" in name
                or ":" in name or any(ord(c) < 32 for c in name)):
            raise ValueError("Invalid inbox filename")
        candidate = inbox / name
        if candidate.is_symlink() or not candidate.is_file():
            raise ValueError("Selected inbox file is missing or unsafe")
        candidates.append(candidate)
    if len(candidates) != len(set(candidates)):
        raise ValueError("Duplicate filenames in request")
    return candidates


def quick_organize_inbox(file_names: list[str] | None = None) -> dict[str, object]:
    """Import only unseen bytes and refresh the register; safely retryable.

    Specified names are the files returned by the existing /api/upload route,
    so unrelated inbox content is never imported as a side effect of a drop.
    The manual inbox button processes a bounded batch of remaining files.
    """
    with _LOCK:
        paths = create_local_workspace()
        inbox = paths.inbox_dir
        if inbox.is_symlink() or not inbox.is_dir():
            raise ValueError("Inbox is not a safe local folder")

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

        if file_names is None:
            candidates = []
            scanned = 0
            for entry in inbox.rglob("*"):
                scanned += 1
                if scanned > _MAX_SCANNED:
                    raise ValueError("Inbox contains too many entries for quick organization")
                if entry.is_symlink():
                    raise ValueError("Inbox contains a symbolic link; review it manually")
                if entry.is_file():
                    candidates.append(entry)
            candidates.sort()
        else:
            candidates = _requested_files(inbox, file_names)

        new_files: list[Path] = []
        skipped = 0
        remaining = 0
        total_size = 0
        for candidate in candidates:
            digest = _digest(candidate)
            if digest in known_hashes:
                skipped += 1
                continue
            file_size = candidate.stat().st_size
            if len(new_files) >= _MAX_FILES or total_size + file_size > _MAX_TOTAL_BYTES:
                if file_names is not None:
                    raise ValueError("Selected files exceed quick-intake limits")
                remaining += 1
                continue
            known_hashes.add(digest)
            total_size += file_size
            new_files.append(candidate)

        if new_files:
            import_sources(None, selected_files=new_files)

        # A previous attempt may have successfully imported but failed during
        # register creation. On retry, always reconcile existing originals.
        if new_files or any(paths.originals_dir.iterdir()):
            build_document_register()

        return {
            "imported_files": len(new_files),
            "already_present": skipped,
            "remaining_files": remaining,
            "register_ready": bool(new_files or (paths.register_dir / "document_register.csv").exists()),
        }
