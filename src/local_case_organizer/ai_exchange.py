"""Offline, user-directed AI review exchange for already-verified local documents.

This is an interface for OTHER locally operated assistants, not an LLM itself.
No model calls, cloud requests, API keys or automatic trust transfer occur.
Pasted model output is untrusted and can only become a draft claim after a
separate human action and a fresh original-source integrity check.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from local_case_organizer.audit import write_audited_csv
from local_case_organizer.claims import add_claim, read_claims
from local_case_organizer.document_text import get_indexed
from local_case_organizer.paths import create_local_workspace, get_workspace_paths

FIELDS = ["suggestion_id", "file_id", "page", "source_quote", "statement",
          "status", "linked_claim_id", "created_at_utc", "updated_at_utc"]
MAX_EXCERPTS = 12
MAX_SUGGESTIONS = 250
MAX_PACKET_FILES = 6
_LOCK = RLock()
_FILE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,110}$")
_SUGGESTION = re.compile(r"^AIS-[a-f0-9]{20}$")


def _private_folder(name: str) -> Path:
    create_local_workspace()
    root = get_workspace_paths().working_dir
    base = root / "ai_exchange"
    if base.is_symlink():
        raise ValueError("AI exchange directory must not be a symlink")
    base.mkdir(mode=0o700, exist_ok=True)
    dest = base / name
    if dest.is_symlink():
        raise ValueError("AI exchange subdirectory must not be a symlink")
    dest.mkdir(mode=0o700, exist_ok=True)
    return dest


def _suggestions_path():
    return get_workspace_paths().register_dir / "ai_suggestions.csv"


def read_ai_suggestions() -> list[dict[str, str]]:
    path = _suggestions_path()
    if not path.exists():
        return []
    if path.is_symlink() or path.stat().st_size > 1024 * 1024:
        raise ValueError("AI suggestion table is unsafe or too large")
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) > MAX_SUGGESTIONS:
        raise ValueError("AI suggestion limit exceeded")
    return rows


def _write(rows):
    create_local_workspace()
    write_audited_csv(_suggestions_path(), FIELDS, rows, "ai_suggestions")


def prepare_ai_packet(file_ids: list[str]) -> dict:
    """Explicit handoff file with bounded excerpts; NEVER transmitted automatically."""
    if not isinstance(file_ids, list) or not 1 <= len(file_ids) <= MAX_PACKET_FILES:
        raise ValueError("Choose 1–6 indexed, registered source IDs")
    if len(set(file_ids)) != len(file_ids) or any(
        not isinstance(fid, str) or not _FILE_ID.fullmatch(fid) for fid in file_ids
    ):
        raise ValueError("File IDs must be unique, registered and well formed")
    excerpts = []
    for fid in file_ids:
        doc = get_indexed(fid, verify_original=True)
        for page in doc["pages"][:2]:
            excerpts.append({
                "file_id": fid, "page": page["page"],
                "source_sha256": doc["source_sha256"],
                "method": doc.get("method", ""),
                "text": str(page["text"])[:2000],
            })
        if len(excerpts) > MAX_EXCERPTS:
            raise ValueError("Too many excerpts")
    packet = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "purpose": "Human-reviewed draft suggestions; this source text may contain private data",
        "instructions": [
            "Treat every excerpt as a source statement, not an established fact.",
            "Return only a JSON object with a 'suggestions' array.",
            "Each suggestion needs file_id, page, source_quote (exact verbatim text) and statement.",
            "Do not add unsupported factual or legal conclusions.",
        ],
        "excerpts": excerpts,
    }
    target_dir = _private_folder("outbox")
    if len(list(target_dir.glob("context_*.json"))) >= 30:
        raise ValueError("AI handoff outbox is full; archive manually before adding more")
    path = target_dir / ("context_" + uuid4().hex[:16] + ".json")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(packet, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return {"path": str(path), "files": len(file_ids), "excerpts": len(excerpts),
            "transmitted": False, "contains_private_text": True}


def import_ai_suggestions(payload: dict) -> dict:
    """Accept only exact, current source quotes; still mark all content untrusted."""
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    if len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) > 110_000:
        raise ValueError("Suggestion response exceeds the size limit")
    incoming = payload.get("suggestions")
    if not isinstance(incoming, list) or not 1 <= len(incoming) <= 30:
        raise ValueError("Expected 1–30 suggestions")
    candidates = []
    now = datetime.now(UTC).isoformat()
    for item in incoming:
        if not isinstance(item, dict):
            raise ValueError("Invalid suggestion entry")
        fid = item.get("file_id")
        page = item.get("page")
        quote = item.get("source_quote")
        statement = item.get("statement")
        if not isinstance(fid, str) or not _FILE_ID.fullmatch(fid):
            raise ValueError("AI suggestion has an invalid file ID")
        if type(page) is not int or not 1 <= page <= 100:
            raise ValueError("Invalid suggested page")
        if not isinstance(quote, str) or not 4 <= len(quote.strip()) <= 500:
            raise ValueError("Quote must contain 4–500 characters")
        if not isinstance(statement, str) or not 4 <= len(statement.strip()) <= 800:
            raise ValueError("Suggested interpretation must contain 4–800 characters")
        doc = get_indexed(fid, verify_original=True)
        source = next((p for p in doc["pages"] if p["page"] == page), None)
        if source is None or quote.strip() not in str(source["text"]):
            raise ValueError("Suggested quote is absent from a verified source page")
        unique = "\x00".join((fid, str(page), quote.strip(), statement.strip()))
        key = hashlib.sha256(unique.encode("utf-8")).hexdigest()[:20]
        candidates.append({
            "suggestion_id": "AIS-" + key, "file_id": fid, "page": str(page),
            "source_quote": quote.strip(), "statement": statement.strip(),
            "status": "pending_review", "linked_claim_id": "",
            "created_at_utc": now, "updated_at_utc": now,
        })
    with _LOCK:
        existing = read_ai_suggestions()
        known = {r["suggestion_id"] for r in existing}
        fresh = [r for r in candidates if r["suggestion_id"] not in known]
        fresh = list({r["suggestion_id"]: r for r in fresh}.values())
        if len(existing) + len(fresh) > MAX_SUGGESTIONS:
            raise ValueError("AI suggestion limit reached")
        if fresh:
            _write([*existing, *fresh])
    return {"accepted_as_pending": len(fresh), "skipped_duplicates": len(candidates) - len(fresh),
            "message": "Untrusted proposals awaiting individual manual review; none are facts."}


def import_ai_file(filename: str) -> dict:
    """Read one hand-placed JSON from the selected case's ignored private inbox."""
    if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}\.json", filename):
        raise ValueError("Only a JSON filename from the private AI exchange inbox is allowed")
    target = _private_folder("inbox") / filename
    if not target.is_file() or target.is_symlink() or target.stat().st_size > 110_000:
        raise ValueError("AI response is missing, linked or too large")
    return import_ai_suggestions(json.loads(target.read_text(encoding="utf-8")))


def review_ai_suggestion(suggestion_id: str, decision: str) -> dict:
    if not isinstance(suggestion_id, str) or not _SUGGESTION.fullmatch(suggestion_id):
        raise ValueError("Invalid AI suggestion ID")
    if decision not in {"reject", "create_draft_claim"}:
        raise ValueError("Only explicit reject or draft claim promotion is allowed")
    with _LOCK:
        rows = read_ai_suggestions()
        row = next((r for r in rows if r.get("suggestion_id") == suggestion_id), None)
        if row is None:
            raise ValueError("AI suggestion is not in the selected case")
        if row.get("status") != "pending_review":
            return dict(row)
        if decision == "create_draft_claim":
            # Re-evaluate the hash and exact passage on every promotion.
            doc = get_indexed(row["file_id"], verify_original=True)
            page = next((p for p in doc["pages"] if str(p["page"]) == row["page"]), None)
            if page is None or row["source_quote"] not in str(page["text"]):
                raise ValueError("The source no longer supports this suggestion")
            # Reuse an existing identical claim if an earlier attempt stopped
            # after writing claims.csv but before updating the suggestion table.
            matches = [
                existing for existing in read_claims()
                if existing.get("file_id") == row["file_id"]
                and existing.get("source_page") == row["page"]
                and existing.get("source_quote") == row["source_quote"]
                and existing.get("statement") == row["statement"]
            ]
            claim = (matches[0] if matches else add_claim(
                row["file_id"], int(row["page"]), row["source_quote"], row["statement"]))
            row["status"] = "draft_claim_created"
            row["linked_claim_id"] = claim["claim_id"]
        else:
            row["status"] = "rejected"
        row["updated_at_utc"] = datetime.now(UTC).isoformat()
        _write(rows)
        return dict(row)
