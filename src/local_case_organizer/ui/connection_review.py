"""Human-reviewed, case-scoped organizational links between verified originals.

This is not a truth, causality, legal-status or knowledge authority. The stored
decision covers an exact set of source references; source or membership drift
invalidates it. All source contents remain in their original case workspace.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

from local_case_organizer.audit import MAX_TABLE_BYTES, write_audited_csv
from local_case_organizer.paths import create_local_workspace, get_workspace_paths
from local_case_organizer.ui.case_connections import linked_document_hints

_FIELDS = ["group_id", "source_signature", "review_status", "reviewed_at"]
_DECISIONS = {"accepted_as_organizational_link", "dismissed"}
_LOCK = RLock()


def _path() -> Path:
    return get_workspace_paths().register_dir / "connection_reviews.csv"


def _read() -> dict[str, dict[str, str]]:
    path = _path()
    if path.is_symlink():
        raise ValueError("Connection review table must not be a symlink")
    if not path.exists():
        return {}
    if not path.is_file() or path.stat().st_size > MAX_TABLE_BYTES:
        raise ValueError("Connection review table is unsafe or too large")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != _FIELDS:
            raise ValueError("Invalid connection review table schema")
        result: dict[str, dict[str, str]] = {}
        for row in reader:
            group_id = str(row.get("group_id", ""))
            signature = str(row.get("source_signature", ""))
            status = str(row.get("review_status", ""))
            if (not re.fullmatch(r"[0-9a-f]{24}", group_id)
                    or not re.fullmatch(r"[0-9a-f]{64}", signature)
                    or status not in _DECISIONS or group_id in result):
                raise ValueError("Invalid connection review record")
            result[group_id] = {key: str(row.get(key, "")) for key in _FIELDS}
            if len(result) > 10000:
                raise ValueError("Connection review table exceeds row limit")
        return result


def _identity(group: dict[str, object]) -> tuple[str, str]:
    # The ID tracks one typed reference. The signature tracks its *current*
    # verified members and exact citations, including page and quotation.
    kind = str(group["reference_kind"])
    ref = str(group["reference"])
    group_id = hashlib.sha256(
        json.dumps([kind, ref], ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:24]
    evidence = sorted(
        (str(doc["file_id"]), int(doc["page"]), str(doc["source_quote"]))
        for doc in group["documents"]
    )
    signature = hashlib.sha256(
        json.dumps([kind, ref, evidence], ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return group_id, signature


def reviewed_document_hints(selected_ids: set[str] | None = None) -> dict[str, object]:
    """Provide read-only reviewed hints. A restricted export cannot reuse a
    full-case decision if any of its members are excluded.
    """
    report = linked_document_hints(selected_ids)
    reviewed = _read()
    for group in report["groups"]:
        group_id, signature = _identity(group)
        record = reviewed.get(group_id)
        group["group_id"] = group_id
        group["source_signature"] = signature
        group["status"] = (
            "pending_review" if record is None
            else record["review_status"] if record["source_signature"] == signature
            else "recheck_required"
        )
        group["reviewed_at"] = (
            record["reviewed_at"] if record and record["source_signature"] == signature
            else ""
        )
        group["review_basis"] = "organizational_only_not_fact_or_legal_review"
    return report


def review_connection(group_id: str, source_signature: str, decision: str) -> dict[str, str]:
    """Accept/dismiss only a freshly source-verified full-case proposal.

    Caller-supplied IDs and signatures are optimistic concurrency tokens, never
    proof. The current source set is re-verified under the review lock.
    """
    if (not isinstance(group_id, str)
            or not re.fullmatch(r"[0-9a-f]{24}", group_id)
            or not isinstance(source_signature, str)
            or not re.fullmatch(r"[0-9a-f]{64}", source_signature)
            or decision not in _DECISIONS):
        raise ValueError("Invalid connection review request")
    with _LOCK:
        groups = reviewed_document_hints()["groups"]
        group = next((item for item in groups if item["group_id"] == group_id), None)
        if group is None or group["source_signature"] != source_signature:
            raise ValueError("Connection sources changed or are not verifiable; refresh first")
        current = _read()
        existing = current.get(group_id)
        if (existing and existing["source_signature"] == source_signature
                and existing["review_status"] == decision):
            return {"group_id": group_id, "status": decision, "reviewed_at": existing["reviewed_at"]}
        create_local_workspace()
        reviewed_at = datetime.now(UTC).isoformat()
        current[group_id] = {
            "group_id": group_id, "source_signature": source_signature,
            "review_status": decision, "reviewed_at": reviewed_at,
        }
        write_audited_csv(_path(), _FIELDS, list(current.values()), "connections")
        return {"group_id": group_id, "status": decision, "reviewed_at": reviewed_at}
