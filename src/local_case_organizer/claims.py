"""Human-reviewed claims tied to hash-verified, indexed source passages."""
from __future__ import annotations

import csv
import os
import re
import tempfile
from threading import RLock
from datetime import UTC, datetime
from uuid import uuid4

from local_case_organizer.document_text import get_indexed
from local_case_organizer.audit import write_audited_csv
from local_case_organizer.paths import create_local_workspace, get_workspace_paths

CLAIM_FIELDS = ["claim_id", "file_id", "source_page", "source_quote",
                "statement", "review_status", "created_at_utc", "reviewed_at_utc"]
STATES = {"draft", "needs_review", "reviewed"}
MAX_CLAIMS = 1500
_CLAIMS_LOCK = RLock()


def _path():
    return get_workspace_paths().register_dir / "claims.csv"


def read_claims() -> list[dict[str, str]]:
    path = _path()
    if not path.exists():
        return []
    if path.is_symlink():
        raise ValueError("Claims table must not be a symlink")
    if path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("Claims table exceeds size limit")
    with path.open("r", encoding="utf-8", newline="") as fd:
        return list(csv.DictReader(fd))


def _write_claims(rows: list[dict[str, str]]) -> None:
    create_local_workspace()
    write_audited_csv(_path(), CLAIM_FIELDS, rows, "claims")


def add_claim(file_id: str, source_page: int, source_quote: str,
              statement: str) -> dict[str, str]:
    if not isinstance(file_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,110}", file_id):
        raise ValueError("Invalid source document ID")
    if not isinstance(source_page, int) or isinstance(source_page, bool) or not 1 <= source_page <= 100:
        raise ValueError("Invalid source page")
    if not isinstance(source_quote, str) or not 4 <= len(source_quote.strip()) <= 500:
        raise ValueError("Source quote must be 4–500 characters")
    if not isinstance(statement, str) or not 4 <= len(statement.strip()) <= 800:
        raise ValueError("Claim statement must be 4–800 characters")
    data = get_indexed(file_id, verify_original=True)
    page = next((item for item in data["pages"]
                 if int(item.get("page", -1)) == source_page), None)
    if page is None or source_quote.strip() not in str(page["text"]):
        raise ValueError("Quote must occur verbatim on the referenced indexed source page")
    with _CLAIMS_LOCK:
        existing = read_claims()
        if len(existing) >= MAX_CLAIMS:
            raise ValueError("Claim limit reached")
        row = {
            "claim_id": "CLM-" + uuid4().hex[:16], "file_id": file_id,
            "source_page": str(source_page), "source_quote": source_quote.strip(),
            "statement": statement.strip(), "review_status": "draft",
            "created_at_utc": datetime.now(UTC).isoformat(), "reviewed_at_utc": "",
        }
        _write_claims([*existing, row])
        return row


def set_review_status(claim_id: str, status: str) -> dict[str, str]:
    if not isinstance(claim_id, str) or not re.fullmatch(r"CLM-[a-f0-9]{16}", claim_id):
        raise ValueError("Invalid claim ID")
    if status not in STATES:
        raise ValueError("Unknown review status")
    with _CLAIMS_LOCK:
        rows = read_claims()
        found = next((row for row in rows if row.get("claim_id") == claim_id), None)
        if found is None:
            raise ValueError("Claim not found")
        if status == "reviewed":
            # Even human-reviewed metadata must retain a currently verified source.
            data = get_indexed(found["file_id"], verify_original=True)
            source = next((page for page in data["pages"] if
                           int(page.get("page", -1)) == int(found["source_page"])), None)
            if source is None or found["source_quote"] not in str(source["text"]):
                raise ValueError("Source no longer supports the recorded quote")
        found["review_status"] = status
        found["reviewed_at_utc"] = datetime.now(UTC).isoformat() if status == "reviewed" else ""
        _write_claims(rows)
        return found
