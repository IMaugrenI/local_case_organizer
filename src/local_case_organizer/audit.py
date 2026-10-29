"""Local metadata-only change journal for editable case CSV tables.

Two-stage records distinguish 'prepared' and 'committed' file replacements.
No user identity is asserted, and file contents are never logged. Not a
cryptographically signed or cross-process transactional audit system.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import tempfile
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from local_case_organizer.paths import get_workspace_paths

_LOCK = RLock()
MAX_LOG_BYTES = 8 * 1024 * 1024
MAX_TABLE_BYTES = 3 * 1024 * 1024
_AREAS = {"register", "timeline", "entities", "claims", "comparisons", "tasks", "ai_suggestions", "connections"}


def _log_path() -> Path:
    return get_workspace_paths().register_dir / "change_audit.jsonl"


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _append_log(event: dict) -> None:
    path = _log_path()
    if path.is_symlink():
        raise ValueError("Audit journal must not be a symlink")
    data = (json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    if path.exists() and path.stat().st_size + len(data) > MAX_LOG_BYTES:
        raise ValueError("Audit journal size limit reached; preserve and archive it manually")
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "ab") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def write_audited_csv(path: Path, fields: list[str], rows: list[dict],
                      area: str) -> Path:
    """Atomic file replace with content-free intent + completion records.

    Failure before the file swap preserves existing rows. A process interruption
    after the swap can leave a 'prepared' journal record; the hash allows
    later diagnosis without falsely stating that the transaction committed.
    """
    if area not in _AREAS:
        raise ValueError("Unknown audited area")
    if not isinstance(rows, list) or len(rows) > 10000:
        raise ValueError("Invalid or excessive CSV row count")
    if not path.parent.is_dir():
        raise FileNotFoundError("Register directory does not exist")
    if not re.fullmatch(r"[a-z_]+\.csv", path.name):
        raise ValueError("Unsupported audited CSV filename")
    with _LOCK:
        if path.is_symlink():
            raise ValueError("Cannot edit symlinked case data")
        if path.exists() and path.stat().st_size > MAX_TABLE_BYTES:
            raise ValueError("Existing case table exceeds size limit")
        before = path.read_bytes() if path.exists() else b""
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})
        updated = buffer.getvalue().encode("utf-8")
        if len(updated) > MAX_TABLE_BYTES:
            raise ValueError("Updated case table exceeds size limit")
        if before == updated:
            return path
        temp = None
        change_id = "AUD-" + uuid4().hex[:16]
        metadata = {
            "change_id": change_id, "at": datetime.now(UTC).isoformat(),
            "area": area, "row_count": len(rows),
            "before_sha256": _digest(before), "after_sha256": _digest(updated),
            "actor": "local_operator_not_authenticated",
        }
        try:
            with tempfile.NamedTemporaryFile("wb", dir=path.parent,
                                             prefix=".audited-", delete=False) as handle:
                temp = handle.name
                os.chmod(temp, 0o600)
                handle.write(updated)
                handle.flush()
                os.fsync(handle.fileno())
            _append_log({**metadata, "stage": "prepared"})
            if path.is_symlink():
                raise ValueError("Case data path became a symlink")
            os.replace(temp, path)
            temp = None
            _append_log({**metadata, "stage": "committed"})
        finally:
            if temp and os.path.exists(temp):
                os.unlink(temp)
        return path


def recent_changes(limit: int = 30) -> list[dict]:
    if not 1 <= limit <= 100:
        raise ValueError("Invalid audit limit")
    path = _log_path()
    if not path.exists():
        return []
    if path.is_symlink() or path.stat().st_size > MAX_LOG_BYTES:
        raise ValueError("Audit journal is unsafe or exceeds size limit")
    latest = deque(maxlen=limit * 3)
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if entry.get("stage") == "committed":
                latest.append({key: entry.get(key) for key in (
                    "change_id", "at", "area", "row_count",
                    "before_sha256", "after_sha256", "actor", "stage")})
    return list(reversed(latest))[:limit]
