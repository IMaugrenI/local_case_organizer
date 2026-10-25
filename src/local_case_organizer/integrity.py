"""Explicit read-only integrity verification with an append-only local result journal."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter, deque
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from local_case_organizer.export.helpers import _resolve_original_path
from local_case_organizer.paths import create_local_workspace, get_workspace_paths


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_integrity(max_files: int = 1000) -> dict[str, object]:
    """Verify imported originals without changing them. Invoke explicitly, never on import."""
    paths = create_local_workspace()
    provenance = paths.register_dir / "provenance.csv"
    if not provenance.exists():
        return {"verified": 0, "results": {}, "journal": "not written; no provenance"}
    if not 1 <= max_files <= 10_000:
        raise ValueError("Invalid verification limit")
    with provenance.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) > max_files:
        raise ValueError("Too many records for this bounded verification; increase the explicit limit")

    checked = set()
    results = []
    for row in rows:
        file_id = str(row.get("file_id", ""))
        expected = str(row.get("sha256", "")).lower()
        relative = str(row.get("stored_relative_path", ""))
        status = "invalid_provenance"
        if file_id and file_id not in checked and relative and len(expected) == 64:
            try:
                source = _resolve_original_path(paths.originals_dir, relative)
                status = "ok" if _digest(source) == expected else "hash_mismatch"
            except FileNotFoundError:
                status = "missing"
            except (OSError, ValueError, RuntimeError):
                status = "invalid_path"
        if file_id in checked:
            status = "duplicate_id"
        checked.add(file_id)
        results.append({"file_id": file_id[:120], "status": status})

    totals = dict(Counter(item["status"] for item in results))
    run_id = uuid4().hex
    timestamp = datetime.now(UTC).isoformat()
    journal = paths.register_dir / "integrity_journal.jsonl"
    # Append-only, no content or absolute file paths. Scope follows current case.
    fd = os.open(journal, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as stream:
        stream.write(json.dumps({"type": "verification", "run_id": run_id,
                                 "at": timestamp, "counts": totals, "checked": len(results)}) + "\n")
        for result in results:
            stream.write(json.dumps({"type": "record", "run_id": run_id, **result}) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return {"verified": len(results), "results": totals, "run_id": run_id,
            "journal": journal.name}


def recent_integrity_runs(limit: int = 8) -> list[dict]:
    journal = get_workspace_paths().register_dir / "integrity_journal.jsonl"
    if not journal.exists():
        return []
    if not 1 <= limit <= 50:
        raise ValueError("Invalid limit")
    # Bounded memory even for many historical checks.
    found = deque(maxlen=limit)
    with journal.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if value.get("type") == "verification":
                found.append(value)
    return list(reversed(found))
