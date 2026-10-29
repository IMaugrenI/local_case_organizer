"""Local, explainable date suggestions for the existing case timeline.

No LLM, OCR, network access, automatic document rewriting, or automatic evidence
assessment. Each proposal includes its exact imported source document and line.
Only a deliberate accept action may add a draft timeline row.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime
from pathlib import Path

from local_case_organizer.document_text import get_indexed
from local_case_organizer.export.helpers import _resolve_original_path, load_provenance_index
from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.timeline.store import read_timeline_rows, write_timeline_rows

MAX_SCAN_FILES = 60
MAX_READ_BYTES = 256 * 1024
MAX_PROPOSALS = 64
MAX_PER_FILE = 6
SUPPORTED = {".txt", ".md", ".csv", ".eml", ".pdf"}
DATE_PATTERN = re.compile(r"(?<![0-9])(?:[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4})(?![0-9])")
HEX_SHA = re.compile(r"^[a-fA-F0-9]{64}$")


def _date_iso(raw: str) -> str | None:
    try:
        when = datetime.strptime(raw, "%Y-%m-%d" if "-" in raw else "%d.%m.%Y")
    except ValueError:
        return None
    # Historical cases may have older dates; deliberately avoid claiming an event is true.
    return when.date().isoformat()


def _verified_lines(path: Path, expected_sha256: str) -> list[str]:
    # Single bounded read: the bytes parsed are exactly the bytes hash-verified.
    with path.open("rb") as stream:
        raw = stream.read(MAX_READ_BYTES + 1)
    if len(raw) > MAX_READ_BYTES:
        raise ValueError("too_large")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("integrity_mismatch")
    if b"\x00" in raw:
        raise ValueError("unsupported_content")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("non_utf8") from exc
    return text.splitlines()[:3500]


def propose_events() -> dict[str, object]:
    """Suggest limited draft events for verified, explicitly registered text originals."""
    paths = get_workspace_paths()
    provenance = load_provenance_index(paths.register_dir)
    rows = read_register_rows()
    candidates: list[dict[str, object]] = []
    warnings: list[dict[str, str]] = []
    visited_ids = set()
    fingerprints: dict[str, list[str]] = {}
    for row in rows[:MAX_SCAN_FILES]:
        file_id = str(row.get("file_id", "")).strip()
        if not file_id or file_id in visited_ids:
            continue
        visited_ids.add(file_id)
        entry = provenance.get(file_id)
        if not entry:
            warnings.append({"file_id": file_id[:100], "reason": "missing_provenance"})
            continue
        relative_path = str(entry.get("stored_relative_path", ""))
        expected = str(entry.get("sha256", "")).lower()
        suffix = Path(str(entry.get("original_name", ""))).suffix.lower()
        if not relative_path or not HEX_SHA.fullmatch(expected):
            warnings.append({"file_id": file_id[:100], "reason": "invalid_provenance"})
            continue
        if suffix not in SUPPORTED:
            # An opt-in OCR / PDF reader may be integrated separately later.
            continue
        try:
            if suffix == ".pdf":
                # PDF suggestions use already indexed text, but reverify the
                # original hash on every read. No PDF or OCR execution here.
                derived = get_indexed(file_id, verify_original=True)
                if derived.get("source_sha256") != expected:
                    raise ValueError("integrity_mismatch")
                chunks = [
                    (int(page["page"]), str(page["text"]).splitlines()[:3500])
                    for page in derived["pages"][:8]
                ]
            else:
                source = _resolve_original_path(paths.originals_dir, relative_path)
                chunks = [(1, _verified_lines(source, expected))]
        except (OSError, ValueError, RuntimeError, TypeError) as exc:
            reason = str(exc)
            if not reason.startswith(("too_large", "integrity_mismatch", "non_utf8", "unsupported_content")):
                reason = "unavailable_or_unsafe_path"
            warnings.append({"file_id": file_id[:100], "reason": reason})
            continue
        fingerprints.setdefault(expected, []).append(file_id)
        count = 0
        for page_no, lines in chunks:
            for line_no, text in enumerate(lines, start=1):
                # Keep proposals bounded and annotate the exact page and line.
                if len(text) > 3000:
                    continue
                for match in DATE_PATTERN.finditer(text):
                    date = _date_iso(match.group(0))
                    if date is None:
                        continue
                    excerpt = " ".join(text.split())[:200]
                    fingerprint = "\x00".join((file_id, str(page_no), str(line_no), date, excerpt))
                    candidate_id = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:20]
                    candidates.append({
                        "candidate_id": candidate_id,
                        "file_id": file_id,
                        "original_name": str(entry.get("original_name", ""))[:120],
                        "page": page_no,
                        "line": line_no,
                        "date": date,
                        "excerpt": excerpt,
                        "method": "source_text_date_mention",
                        "review_status": "suggested_not_verified",
                    })
                    count += 1
                    if count >= MAX_PER_FILE or len(candidates) >= MAX_PROPOSALS:
                        break
                if count >= MAX_PER_FILE or len(candidates) >= MAX_PROPOSALS:
                    break
            if count >= MAX_PER_FILE or len(candidates) >= MAX_PROPOSALS:
                break
        if len(candidates) >= MAX_PROPOSALS:
            break
    duplicates = [
        {"sha256_prefix": digest[:12], "file_ids": ids}
        for digest, ids in fingerprints.items() if len(ids) > 1
    ]
    return {
        "candidates": candidates,
        "warnings": warnings[:80],
        "duplicate_content": duplicates[:30],
        "limits": {"max_files": MAX_SCAN_FILES, "max_file_bytes": MAX_READ_BYTES,
                   "max_candidates": MAX_PROPOSALS},
        "note": "Dates are text matches, NOT verified events. Only a manual accept adds a draft.",
    }


def accept_candidate(candidate_id: str) -> dict[str, str]:
    """Recompute from the original before acceptance. Never trust UI-supplied text."""
    if not isinstance(candidate_id, str) or not re.fullmatch("[a-f0-9]{20}", candidate_id):
        raise ValueError("Invalid suggestion identifier")
    proposal = next((item for item in propose_events()["candidates"]
                     if item["candidate_id"] == candidate_id), None)
    if proposal is None:
        raise ValueError("Suggestion is unavailable, stale or its source failed integrity checks")
    event_id = "EV-SUG-" + candidate_id
    existing = read_timeline_rows()
    if any(row.get("event_id") == event_id for row in existing):
        return {"status": "already_recorded", "event_id": event_id}
    if len(existing) >= 5000:
        raise ValueError("Timeline row limit reached")
    excerpt = str(proposal["excerpt"])
    updated = list(existing) + [{
        "event_id": event_id,
        "event_date": str(proposal["date"]),
        "event_title": ("Review suggested event: " + excerpt)[:160],
        "linked_file_ids": str(proposal["file_id"]),
        "people_or_entities": "",
        "summary": f"Unverified date mention, page {proposal['page']}, line {proposal['line']}: {excerpt}",
        "status": "draft",
    }]
    write_timeline_rows(updated)
    return {"status": "draft_added", "event_id": event_id, "file_id": str(proposal["file_id"])}
