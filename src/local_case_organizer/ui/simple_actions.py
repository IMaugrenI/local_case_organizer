"""Small, explicit UI actions composing the existing case stores.

Only user-requested edits are performed. All changes use existing audited
register/timeline writers; no document contents, OCR, LLMs or exports are
processed by these helpers.
"""
from __future__ import annotations

from datetime import date
from threading import RLock
from uuid import uuid4

from local_case_organizer.entities.store import read_entity_rows, write_entity_rows
from local_case_organizer.document_text import (
    MAX_INPUT_BYTES, TEXT_SUFFIXES, get_indexed, index_document,
)
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.timeline.store import read_timeline_rows, write_timeline_rows

_EDIT_LOCK = RLock()
_STATUSES = {"unreviewed", "reviewed", "flagged", "selected_for_export"}
_UPDATE_FIELDS = {"selected_for_export", "review_status", "note", "document_group"}
_INDEXABLE = TEXT_SUFFIXES | {".pdf"}


def update_document(payload: dict) -> dict[str, str]:
    """Patch exactly one editable field without trusting client-side CSV rows."""
    if not isinstance(payload, dict) or set(payload) != {"file_id", "field", "value"}:
        raise ValueError("One document ID, editable field and value are required")
    file_id, field, value = payload["file_id"], payload["field"], payload["value"]
    if (not isinstance(file_id, str) or len(file_id) > 110
            or not isinstance(field, str) or field not in _UPDATE_FIELDS
            or not isinstance(value, str)):
        raise ValueError("Invalid document update")
    if field == "selected_for_export" and value not in {"yes", "no"}:
        raise ValueError("Export selection must be yes or no")
    if field == "review_status" and value not in _STATUSES:
        raise ValueError("Invalid review status")
    if field == "note" and len(value) > 1200:
        raise ValueError("Note exceeds 1200 characters")
    if field == "document_group" and len(value) > 120:
        raise ValueError("Document category exceeds 120 characters")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in value):
        raise ValueError("Invalid control character")

    with _EDIT_LOCK:
        rows = read_register_rows()
        matches = [row for row in rows if row.get("file_id") == file_id]
        if len(matches) != 1:
            raise ValueError("Document is missing or has ambiguous ID")
        matches[0][field] = value
        write_register_rows(rows)
    return {"file_id": file_id, "field": field, "value": value}


def add_manual_event(payload: dict) -> dict[str, str]:
    """Append an explicitly operator-entered event as an unverified draft."""
    if not isinstance(payload, dict):
        raise ValueError("Invalid event")
    title = payload.get("title", "")
    event_date = payload.get("date", "")
    summary = payload.get("summary", "")
    file_id = payload.get("file_id", "")
    if not all(isinstance(item, str) for item in (title, event_date, summary, file_id)):
        raise ValueError("Event fields must be text")
    title = title.strip()
    if not 3 <= len(title) <= 160 or len(summary) > 800:
        raise ValueError("Event title or summary length is invalid")
    try:
        parsed = date.fromisoformat(event_date)
    except (ValueError, TypeError) as exc:
        raise ValueError("Event date must be YYYY-MM-DD") from exc
    if parsed.isoformat() != event_date:
        raise ValueError("Use canonical YYYY-MM-DD")
    if file_id and file_id not in {row.get("file_id") for row in read_register_rows()}:
        raise ValueError("Source document is not in this case")

    row = {
        "event_id": "EV-MAN-" + uuid4().hex[:16],
        "event_date": event_date,
        "event_title": title,
        "linked_file_ids": file_id,
        "people_or_entities": "",
        "summary": summary,
        "status": "draft",
    }
    with _EDIT_LOCK:
        rows = read_timeline_rows()
        if len(rows) >= 5000:
            raise ValueError("Timeline row limit reached")
        write_timeline_rows([*rows, row])
    return {"event_id": row["event_id"], "status": "draft"}


def add_manual_entity(payload: dict) -> dict[str, str]:
    """Record a manually named person/institution, without inferred relations."""
    if not isinstance(payload, dict):
        raise ValueError("Invalid entity")
    name = payload.get("name", "")
    kind = payload.get("kind", "")
    notes = payload.get("notes", "")
    file_id = payload.get("file_id", "")
    if not all(isinstance(item, str) for item in (name, kind, notes, file_id)):
        raise ValueError("Entity fields must be text")
    name, kind = name.strip(), kind.strip()
    if not 2 <= len(name) <= 160 or len(kind) > 80 or len(notes) > 1200:
        raise ValueError("Entity fields are too long or missing")
    if file_id and file_id not in {row.get("file_id") for row in read_register_rows()}:
        raise ValueError("Document reference is not in this case")
    row = {
        "entity_id": "EN-MAN-" + uuid4().hex[:16],
        "entity_name": name,
        "entity_type": kind,
        "linked_file_ids": file_id,
        "notes": notes,
    }
    with _EDIT_LOCK:
        existing = read_entity_rows()
        if len(existing) >= 5000:
            raise ValueError("Entity limit reached")
        write_entity_rows([*existing, row])
    return {"entity_id": row["entity_id"], "status": "recorded"}


def prepare_local_search(*, max_files: int = 6, include_pdf: bool = True) -> dict[str, object]:
    """On demand, index a bounded number of registered text/PDF originals.

    Never enable OCR, install dependencies, or accept extracted text as proof.
    Files needing unsupported tools remain safely unindexed, reported as
    warnings. No background work and no external requests.
    """
    if not 1 <= max_files <= 8:
        raise ValueError("Invalid indexing batch size")
    indexed = 0
    already_indexed = 0
    warnings: list[str] = []
    remaining = 0
    for row in read_register_rows():
        file_id = row.get("file_id", "")
        suffix = str(row.get("suffix", "")).lower()
        try:
            size = int(row.get("size_bytes", 0))
        except (TypeError, ValueError):
            continue
        if not file_id or suffix not in _INDEXABLE or (suffix == ".pdf" and not include_pdf) or size > MAX_INPUT_BYTES:
            continue
        try:
            get_indexed(file_id, verify_original=True)
            already_indexed += 1
            continue
        except (ValueError, OSError):
            pass
        if indexed + len(warnings) >= max_files:
            remaining += 1
            continue
        try:
            index_document(file_id, use_ocr=False)
            indexed += 1
        except (ValueError, OSError):
            warnings.append(file_id)
    return {
        "indexed": indexed,
        "already_indexed": already_indexed,
        "skipped_files": warnings,
        "remaining": remaining,
        "note": "Local text extraction only; no OCR or network",
    }
