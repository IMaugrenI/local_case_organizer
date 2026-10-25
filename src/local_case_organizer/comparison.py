"""Manually grouped, source-bound claim value comparisons; never truth judgments."""
from __future__ import annotations

import csv
import os
import re
import tempfile
from datetime import datetime, UTC
from decimal import Decimal, InvalidOperation
from threading import RLock
from uuid import uuid4

from local_case_organizer.claims import read_claims
from local_case_organizer.document_text import get_indexed
from local_case_organizer.audit import write_audited_csv
from local_case_organizer.paths import create_local_workspace, get_workspace_paths

FIELDS = ["comparison_id", "claim_id", "topic", "kind", "value", "normalized",
          "created_at_utc"]
KINDS = {"date", "amount", "text"}
LIMIT = 600
_LOCK = RLock()


def _path():
    return get_workspace_paths().register_dir / "claim_comparisons.csv"


def _canonical(kind, value):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 120:
        raise ValueError("Comparison value length must be 1–120")
    raw = value.strip()
    if kind == "date":
        for format_ in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(raw, format_).date().isoformat()
            except ValueError:
                pass
        raise ValueError("Date must be YYYY-MM-DD or DD.MM.YYYY")
    if kind == "amount":
        # Locale-explicit: decimal comma or decimal point, optional thousands
        # separators. No currency conversion or implicit units.
        if not re.fullmatch(r"-?[0-9]+(?:[.,][0-9]{1,2})?", raw):
            raise ValueError("Amount must be an ungrouped decimal number (e.g. 1250,00)")
        try:
            return str(Decimal(raw.replace(",", ".")).normalize())
        except InvalidOperation as exc:
            raise ValueError("Invalid decimal amount") from exc
    return " ".join(raw.casefold().split())


def read_comparisons():
    path = _path()
    if not path.exists():
        return []
    if path.is_symlink() or path.stat().st_size > 900_000:
        raise ValueError("Comparison table is unsafe or too large")
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _save(rows):
    create_local_workspace()
    write_audited_csv(_path(), FIELDS, rows, "comparisons")


def add_comparison(claim_id: str, topic: str, kind: str, value: str):
    if not isinstance(topic, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", topic):
        raise ValueError("Topic must be a lowercase comparison key, maximum 64 characters")
    if kind not in KINDS:
        raise ValueError("Invalid comparison kind")
    if not isinstance(claim_id, str) or not re.fullmatch(r"CLM-[a-f0-9]{16}", claim_id):
        raise ValueError("Invalid claim ID")
    normalized = _canonical(kind, value)
    with _LOCK:
        claims = read_claims()
        claim = next((row for row in claims if row.get("claim_id") == claim_id), None)
        if claim is None:
            raise ValueError("Claim is not registered in this case")
        # Source hash and exact quote must still be valid at linking time.
        page = get_indexed(claim["file_id"], verify_original=True)
        source = next((row for row in page["pages"]
                       if str(row.get("page")) == str(claim["source_page"])), None)
        if not source or claim["source_quote"] not in source["text"]:
            raise ValueError("Claim quote no longer matches a verified source")
        rows = read_comparisons()
        if len(rows) >= LIMIT:
            raise ValueError("Comparison limit reached")
        if any(row["claim_id"] == claim_id and row["topic"] == topic for row in rows):
            raise ValueError("A claim already has a comparison value for this topic")
        if any(row["topic"] == topic and row["kind"] != kind for row in rows):
            raise ValueError("Cannot mix value kinds under the same comparison topic")
        item = {
            "comparison_id": "CMP-" + uuid4().hex[:16], "claim_id": claim_id,
            "topic": topic, "kind": kind, "value": value.strip(),
            "normalized": normalized, "created_at_utc": datetime.now(UTC).isoformat(),
        }
        _save([*rows, item])
        return item


def comparison_report():
    """Different values for an explicitly shared topic, not a factual contradiction."""
    claims = {row.get("claim_id"): row for row in read_claims()}
    records = read_comparisons()
    groups = {}
    for entry in records:
        key = (entry.get("topic", ""), entry.get("kind", ""))
        groups.setdefault(key, []).append(entry)
    review = []
    for (topic, kind), rows in sorted(groups.items()):
        if len(rows) < 2:
            continue
        file_ids = {claims.get(row["claim_id"], {}).get("file_id") for row in rows}
        values = {row["normalized"] for row in rows}
        if len(file_ids - {None}) < 2 or len(values) < 2:
            continue
        review.append({
            "topic": topic, "kind": kind, "status": "potential_mismatch_needs_human_review",
            "sources": [{
                "claim_id": row["claim_id"],
                "file_id": claims.get(row["claim_id"], {}).get("file_id", ""),
                "value": row["value"], "normalized": row["normalized"],
                "claim_review_status": claims.get(row["claim_id"], {}).get("review_status", "unknown"),
            } for row in rows[:40]],
        })
    return {"records": records, "review_candidates": review[:80],
            "message": "Different manually grouped source statements; no automated truth or legal assessment."}
