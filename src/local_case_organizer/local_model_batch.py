"""Case-scoped, resumable opt-in local model review of indexed sources.

This is called only after the operator explicitly starts a review from the UI.
The UI drives one document per request, keeping stop/resume responsive. A
private progress journal stores model name, source hashes and statuses only.
No original bytes, prompts or model excerpts are kept in this journal.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from threading import Lock

from local_case_organizer.document_text import _index_path
from local_case_organizer.local_model import propose_with_local_model
from local_case_organizer.paths import create_local_workspace
from local_case_organizer.register.store import read_register_rows

_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,99}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_LOCK = Lock()
_MAX_ITEMS = 300


def _progress_path(model: str):
    if not isinstance(model, str) or not _MODEL.fullmatch(model):
        raise ValueError("Invalid local model selection")
    root = create_local_workspace().working_dir
    if root.is_symlink():
        raise ValueError("Unsafe case working directory")
    folder = root / "ai_exchange"
    if folder.is_symlink():
        raise ValueError("Unsafe model progress directory")
    folder.mkdir(mode=0o700, exist_ok=True)
    digest = hashlib.sha256(model.encode("utf-8")).hexdigest()[:24]
    return folder / ("local_model_" + digest + ".json")


def _load(path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    if path.is_symlink() or path.stat().st_size > 90_000:
        raise ValueError("Unsafe local AI progress record")
    item = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(item, dict) or item.get("version") != 1 or not isinstance(item.get("records"), dict):
        raise ValueError("Invalid local AI progress record")
    return {
        str(k): v for k, v in item["records"].items()
        if isinstance(v, dict) and v.get("status") in ("done", "failed")
        and isinstance(v.get("sha256"), str) and _SHA.fullmatch(v["sha256"])
    }


def _save(path, records: dict[str, dict[str, str]]) -> None:
    if len(records) > _MAX_ITEMS:
        raise ValueError("Too many local AI progress records")
    data = json.dumps({"version": 1, "records": records}, sort_keys=True).encode("utf-8")
    if len(data) > 90_000:
        raise ValueError("Local AI progress exceeds bounded size")
    temp = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=path.parent,
                                         prefix=".local-model-", delete=False) as file:
            temp = file.name
            os.chmod(temp, 0o600)
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        if path.is_symlink():
            raise ValueError("Local AI progress file became unsafe")
        os.replace(temp, path)
        temp = None
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)


def _eligible_rows():
    registered = read_register_rows()
    candidates = []
    for row in registered:
        fid = str(row.get("file_id", ""))
        digest = str(row.get("sha256", "")).lower()
        if not fid or not _SHA.fullmatch(digest):
            continue
        try:
            index = _index_path(fid)
        except ValueError:
            continue
        if index.exists() and index.is_file() and not index.is_symlink():
            candidates.append((fid, digest))
        if len(candidates) >= _MAX_ITEMS:
            break
    return candidates


def analyze_next_local_source(model: str, *, retry_failed: bool = False) -> dict[str, object]:
    """Review one remaining indexed source, never an arbitrary local path.

    An unsuccessful source is recorded as failed and not retried automatically.
    Model unavailability stops the current UI session rather than spamming calls.
    """
    if type(retry_failed) is not bool:
        raise ValueError("Invalid retry setting")
    if not _LOCK.acquire(blocking=False):
        raise ValueError("Another case-wide local AI review is active")
    try:
        path = _progress_path(model)
        records = _load(path)
        rows = _eligible_rows()
        processed = 0
        added = 0
        last_error = False
        for fid, digest in rows:
            old = records.get(fid)
            if old and old["sha256"] == digest:
                if old["status"] == "done":
                    continue
                if old["status"] == "failed" and not retry_failed:
                    continue
            try:
                result = propose_with_local_model(model, [fid])
                added = int(result.get("accepted_as_pending", 0))
                status = "done"
            except (ValueError, OSError):
                # Do not write model error details, source passages or prompts.
                status = "failed"
                last_error = True
            records[fid] = {"sha256": digest, "status": status}
            processed = 1
            _save(path, records)
            break
        # Drop obsolete metadata when a case is edited or reimported.
        current = {fid: digest for fid, digest in rows}
        records = {fid: value for fid, value in records.items()
                   if current.get(fid) == value.get("sha256")}
        counts = {"done": 0, "failed": 0, "remaining": 0}
        for fid, digest in rows:
            row = records.get(fid)
            if not row or row.get("sha256") != digest:
                counts["remaining"] += 1
            else:
                counts[row["status"]] += 1
        if retry_failed:
            counts["remaining"] += counts["failed"]
        return {
            "total": len(rows), **counts, "processed_in_step": processed,
            "new_pending_suggestions": added,
            "last_source_failed": last_error,
            "all_results_need_review": True,
        }
    finally:
        _LOCK.release()
