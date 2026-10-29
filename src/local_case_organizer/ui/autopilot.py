"""Bounded, resumable local case preparation after explicit user input.

Existing evidence originals, imported provenance and registered metadata are
never changed by this worker. Only derived text indexes and a private, case-
scoped progress journal are written. No LLM, cloud or automatic export.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from threading import RLock

from local_case_organizer.document_text import (
    ALLOWED_SUFFIXES, IMAGE_SUFFIXES, MAX_INPUT_BYTES, get_indexed, index_document,
)
from local_case_organizer.paths import create_local_workspace
from local_case_organizer.register.store import read_register_rows

_LOCK = RLock()
_MAX_DOCS = 2500
_MAX_STATE_BYTES = 2 * 1024 * 1024
_BATCH_LIMIT = 4
_HEX = re.compile(r"^[a-fA-F0-9]{64}$")
_STATUSES = {"indexed", "needs_ocr", "failed", "skipped"}


def _journal_path() -> Path:
    workspace = create_local_workspace()
    if workspace.working_dir.is_symlink():
        raise ValueError("Unsafe private processing directory")
    return workspace.working_dir / "autopilot_state.json"


def _read_journal() -> dict[str, dict[str, str]]:
    path = _journal_path()
    if not path.exists():
        return {}
    if path.is_symlink() or path.stat().st_size > _MAX_STATE_BYTES:
        raise ValueError("Unsafe or oversized processing journal")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("version") != 1 or not isinstance(obj.get("documents"), dict):
        raise ValueError("Invalid processing journal")
    entries = obj["documents"]
    if len(entries) > _MAX_DOCS:
        raise ValueError("Too many processing journal entries")
    return {str(k): v for k, v in entries.items()
            if isinstance(v, dict) and v.get("status") in _STATUSES
            and isinstance(v.get("sha256"), str) and _HEX.fullmatch(v["sha256"])}


def _save_journal(entries: dict[str, dict[str, str]]) -> None:
    if len(entries) > _MAX_DOCS:
        raise ValueError("Processing journal has reached its limit")
    target = _journal_path()
    raw = json.dumps({"version": 1, "documents": entries},
                     ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(raw) > _MAX_STATE_BYTES:
        raise ValueError("Processing journal exceeds safe size limit")
    temp = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=target.parent,
                                         prefix=".autopilot-", delete=False) as handle:
            temp = handle.name
            os.chmod(temp, 0o600)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if target.is_symlink():
            raise ValueError("Processing journal became a symlink")
        os.replace(temp, target)
        temp = None
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)


def _rows() -> list[dict[str, str]]:
    rows = read_register_rows()
    if len(rows) > _MAX_DOCS:
        raise ValueError("Case exceeds bounded processing limit")
    return rows


def _state(row: dict[str, str], entries: dict[str, dict[str, str]]) -> str:
    file_id = str(row.get("file_id", ""))
    digest = str(row.get("sha256", "")).lower()
    if not file_id or not _HEX.fullmatch(digest):
        return "skipped"
    suffix = str(row.get("suffix", "")).lower()
    if suffix not in ALLOWED_SUFFIXES:
        return "skipped"
    try:
        size = int(row.get("size_bytes", 0))
    except (ValueError, TypeError):
        return "skipped"
    if size < 0 or size > MAX_INPUT_BYTES:
        return "skipped"
    saved = entries.get(file_id)
    if saved and saved.get("sha256") == digest:
        return str(saved.get("status", "pending"))
    return "pending"


def _snapshot(rows: list[dict[str, str]], entries: dict[str, dict[str, str]],
              *, use_ocr: bool) -> dict[str, object]:
    counts = {key: 0 for key in ("indexed", "needs_ocr", "failed", "skipped", "pending")}
    warnings: list[dict[str, str]] = []
    for row in rows:
        status = _state(row, entries)
        counts[status] += 1
        if status in {"needs_ocr", "failed"} and len(warnings) < 20:
            warnings.append({
                "file_id": str(row.get("file_id", ""))[:110],
                "original_name": str(row.get("original_name", ""))[:160],
                "reason": status,
            })
    return {
        "total": len(rows), **counts, "ocr_enabled_for_run": use_ocr,
        "warnings": warnings, "completed": counts["indexed"] + counts["skipped"],
        "manual_review_required": True,
    }


def autopilot_status() -> dict[str, object]:
    """Read-only progress; never launch processing on page load."""
    with _LOCK:
        return _snapshot(_rows(), _read_journal(), use_ocr=False)


def process_autopilot(*, use_ocr: bool = False, retry_failed: bool = False) -> dict[str, object]:
    """Process one limited batch; browser may repeat calls while work remains.

    OCR is enabled only if explicitly selected by the operator.
    Unprocessable sources are reported rather than retried forever.
    """
    if type(use_ocr) is not bool or type(retry_failed) is not bool:
        raise ValueError("Processing options must be booleans")
    with _LOCK:
        rows = _rows()
        journal = _read_journal()
        processed = 0
        for row in rows:
            if processed >= _BATCH_LIMIT:
                break
            file_id = str(row.get("file_id", ""))
            status = _state(row, journal)
            suffix = str(row.get("suffix", "")).lower()
            if status in {"skipped", "indexed"}:
                continue
            if status == "failed" and not retry_failed:
                continue
            if status == "needs_ocr" and not use_ocr:
                continue
            digest = str(row["sha256"]).lower()
            if suffix in IMAGE_SUFFIXES and not use_ocr:
                journal[file_id] = {"sha256": digest, "status": "needs_ocr"}
                processed += 1
                continue
            try:
                result = index_document(file_id, use_ocr=use_ocr)
                if int(result.get("characters", 0)) == 0:
                    journal[file_id] = {"sha256": digest, "status": "failed" if use_ocr else "needs_ocr"}
                else:
                    get_indexed(file_id, verify_original=True)
                    journal[file_id] = {"sha256": digest, "status": "indexed"}
            except (OSError, ValueError) as exc:
                message = str(exc).lower()
                may_need_ocr = (suffix == ".pdf" and not use_ocr
                                and any(word in message for word in ("extract", "ocr", "pdf text")))
                journal[file_id] = {
                    "sha256": digest,
                    "status": "needs_ocr" if may_need_ocr else "failed",
                }
            processed += 1
        # Keep progress scoped to currently registered document IDs.
        allowed = {str(row.get("file_id", "")) for row in rows}
        journal = {k: v for k, v in journal.items() if k in allowed}
        _save_journal(journal)
        report = _snapshot(rows, journal, use_ocr=use_ocr)
        report["processed_in_batch"] = processed
        # For a one-off retry call, failed files do not force infinite loops.
        report["remaining"] = sum(
            1 for row in rows if (
                _state(row, journal) == "pending" or
                (_state(row, journal) == "needs_ocr" and use_ocr)
            )
        )
        return report
