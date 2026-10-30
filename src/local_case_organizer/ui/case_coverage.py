"""A13: Read-only coverage of registered local case sources and manual links.

Coverage means only "what is inspectable among registered local sources";
it cannot attest that all real-world evidence has been supplied. No original,
index, case register, review status or export is changed by this report.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from local_case_organizer.claims import read_claims
from local_case_organizer.document_text import (
    ALLOWED_SUFFIXES, MAX_INPUT_BYTES, get_indexed,
)
from local_case_organizer.entities.store import read_entity_rows
from local_case_organizer.export.helpers import _resolve_original_path, load_provenance_index
from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.tasks import read_tasks
from local_case_organizer.timeline.store import read_timeline_rows

MAX_SCANNED = 120
MAX_EXAMPLES = 40
MAX_VERIFY_BYTES = 32 * 1024 * 1024
_ID = re.compile(r"[a-zA-Z0-9_-]{1,110}\Z")
_SHA = re.compile(r"[0-9a-fA-F]{64}\Z")


def _digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def _source_status(row: dict[str, str], provenance: dict[str, dict[str, str]],
                   originals_dir: Path) -> str:
    """Verify the original before giving any text-index coverage credit."""
    file_id = str(row.get("file_id", ""))
    proof = provenance.get(file_id)
    expected = str(row.get("sha256", ""))
    if not proof or not _SHA.fullmatch(expected):
        return "provenance_unavailable"
    if (str(proof.get("sha256", "")).lower() != expected.lower()
            or not str(proof.get("stored_relative_path", ""))):
        return "provenance_unavailable"
    try:
        source = _resolve_original_path(
            originals_dir, str(proof["stored_relative_path"])
        )
        if source.stat().st_size > MAX_VERIFY_BYTES:
            return "verification_size_limit"
        if _digest(source) != expected.lower():
            return "original_changed"
    except FileNotFoundError:
        return "original_missing"
    except (OSError, ValueError, RuntimeError):
        return "original_unavailable"

    suffix = Path(str(row.get("original_name", ""))).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        return "unsupported_text_format"
    if source.stat().st_size > MAX_INPUT_BYTES:
        return "extraction_size_limit"
    try:
        index = get_indexed(file_id, verify_original=True)
    except (OSError, ValueError, TypeError):
        return "index_needed"
    return ("source_text_available"
            if any(str(page.get("text", "")).strip() for page in index["pages"])
            else "index_has_no_text")


def _linked_ids(raw: object) -> set[str]:
    return {item.strip() for item in str(raw or "").split(",") if item.strip()}


def _manual_coverage(known: set[str]) -> dict[str, object]:
    """Identify only explicit links and unlinked manual entries.

    Neither absence of a link nor a date mentioned in a source proves that a
    real-world document or event is missing.
    """
    groups = (
        ("timeline", read_timeline_rows(), "linked_file_ids"),
        ("entities", read_entity_rows(), "linked_file_ids"),
        ("tasks", read_tasks(), "linked_file_ids"),
        ("claims", read_claims(), "file_id"),
    )
    summary: dict[str, dict[str, int]] = {}
    unrecognized: set[str] = set()
    for name, rows, field in groups:
        without_link = invalid_links = 0
        for row in rows:
            links = _linked_ids(row.get(field, ""))
            if not links:
                without_link += 1
            else:
                unknown = links.difference(known)
                if unknown:
                    invalid_links += 1
                    unrecognized.update(ref for ref in unknown if _ID.fullmatch(ref))
        summary[name] = {
            "entries": len(rows),
            "without_document_link": without_link,
            "with_unknown_document_link": invalid_links,
        }
    return {
        "areas": summary,
        "unknown_document_ids": sorted(unrecognized)[:MAX_EXAMPLES],
        "unknown_ids_truncated": len(unrecognized) > MAX_EXAMPLES,
        "limitations": "Manual links indicate organization only; no missing real-world evidence can be inferred.",
    }


def case_coverage() -> dict[str, object]:
    """Bounded, case-scoped observation of current registered originals."""
    paths = get_workspace_paths()
    rows = read_register_rows()
    known = {str(row.get("file_id", "")) for row in rows if row.get("file_id")}
    prov = load_provenance_index(paths.register_dir)
    counts: Counter[str] = Counter()
    examined: list[dict[str, str]] = []
    for row in rows[:MAX_SCANNED]:
        file_id = str(row.get("file_id", ""))
        if not file_id or not _ID.fullmatch(file_id):
            status = "invalid_register_id"
        else:
            status = _source_status(row, prov, paths.originals_dir)
        counts[status] += 1
        examined.append({
            "file_id": file_id[:110],
            "original_name": str(row.get("original_name", ""))[:140],
            "status": status,
            "review_status": str(row.get("review_status", "unreviewed"))[:40],
            "selected_for_export": (
                "yes" if str(row.get("selected_for_export", "")).lower() == "yes"
                else "no"
            ),
        })
    # Show blockers first, but do not imply verified status for unscanned items.
    rank = {"original_changed": 0, "original_missing": 0, "original_unavailable": 0,
            "provenance_unavailable": 0, "invalid_register_id": 0,
            "verification_size_limit": 1, "extraction_size_limit": 1,
            "index_needed": 2, "index_has_no_text": 2,
            "unsupported_text_format": 2, "source_text_available": 3}
    examined.sort(key=lambda item: (
        rank.get(item["status"], 9), item["original_name"], item["file_id"]
    ))
    skipped = max(0, len(rows) - MAX_SCANNED)
    manual = _manual_coverage(known)
    return {
        "scope": "active_local_case_registered_sources_only",
        "total_registered": len(rows),
        "scanned": len(rows) - skipped,
        "not_scanned": skipped,
        "counts": dict(counts),
        "source_samples": examined[:MAX_EXAMPLES],
        "sample_truncated": len(examined) > MAX_EXAMPLES,
        "manual_links": manual,
        "incomplete": bool(skipped or any(
            key != "source_text_available" and number
            for key, number in counts.items()
        )),
        "limitations": {
            "does_not_prove_real_world_file_completeness": True,
            "does_not_establish_truth_or_legal_findings": True,
            "a_missing_index_does_not_mean_missing_original": True,
            "scan_is_bounded_without_ocr_or_ai": True,
            "no_automatic_review_export_or_write": True,
        },
    }
