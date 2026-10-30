"""A15: Read-only quality snapshot for an explicitly selected lawyer handoff.

Only selected registered originals can appear in the report. A passing local
checksum says nothing about factual truth, legal status or completeness of all
real-world evidence. No background processing, OCR, AI, export, or data writes.
"""
from __future__ import annotations

import re
from pathlib import Path

from local_case_organizer.claims import read_claims
from local_case_organizer.document_text import get_indexed
from local_case_organizer.entities.store import read_entity_rows
from local_case_organizer.export.helpers import (
    _resolve_original_path, _sha256_for_file, load_provenance_index,
)
from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.tasks import read_tasks
from local_case_organizer.timeline.store import read_timeline_rows

MAX_PREVIEW_SOURCES = 120
MAX_WARNINGS = 30
_SHA = re.compile(r"[a-fA-F0-9]{64}\Z")


def _links(value: object) -> set[str]:
    return {item.strip() for item in str(value or "").split(",") if item.strip()}


def _within_selection(row: dict[str, str], selected: set[str]) -> bool:
    """A mixed-source free-text record must never leak into a restricted handoff."""
    linked = _links(row.get("linked_file_ids", ""))
    return bool(linked) and linked.issubset(selected)


def _source_state(file_id: str, proof: dict[str, dict[str, str]], root: Path) -> str:
    provenance = proof.get(file_id)
    if not provenance:
        return "missing_provenance"
    digest = str(provenance.get("sha256", ""))
    if not _SHA.fullmatch(digest):
        return "missing_provenance"
    try:
        source = _resolve_original_path(root, str(provenance.get("stored_relative_path", "")))
        return "verified" if _sha256_for_file(source) == digest.lower() else "hash_mismatch"
    except FileNotFoundError:
        return "missing_original"
    except (ValueError, OSError, RuntimeError):
        return "unsafe_original"


def verified_selected_claim_ids(selected: set[str]) -> set[str]:
    """Select claims with a current hash-matching original and verbatim page quote.

    A past human review status is not substitute for current source support.
    Used in *all* lawyer handoff claim surfaces, not merely the preview.
    """
    supported: set[str] = set()
    cache: dict[str, dict | None] = {}
    for row in read_claims()[:1500]:
        fid = str(row.get("file_id", ""))
        if fid not in selected:
            continue
        if fid not in cache:
            try:
                cache[fid] = get_indexed(fid, verify_original=True)
            except (ValueError, OSError, TypeError):
                cache[fid] = None
        indexed = cache[fid]
        quote = str(row.get("source_quote", "")).strip()
        if not indexed or not quote:
            continue
        if any(
            str(page.get("page", "")) == str(row.get("source_page", ""))
            and quote in str(page.get("text", ""))
            for page in indexed["pages"]
        ):
            supported.add(str(row.get("claim_id", "")))
    return supported


def handoff_quality() -> dict[str, object]:
    """Selected-only, bounded preview; does not mutate source or review state."""
    selected_rows = [
        row for row in read_register_rows()
        if str(row.get("selected_for_export", "")).lower() == "yes"
    ]
    selected = {str(row.get("file_id", "")) for row in selected_rows}
    paths = get_workspace_paths()
    proof = load_provenance_index(paths.register_dir)
    inspected = selected_rows[:MAX_PREVIEW_SOURCES]
    warnings: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    per_source = []
    for row in inspected:
        fid = str(row.get("file_id", ""))[:110]
        status = _source_state(fid, proof, paths.originals_dir)
        counts[status] = counts.get(status, 0) + 1
        review_status = str(row.get("review_status", "unreviewed") or "unreviewed")
        if review_status not in {"reviewed", "selected_for_export"}:
            counts["manual_review_pending"] = counts.get("manual_review_pending", 0) + 1
        per_source.append({
            "file_id": fid,
            "original_name": str(row.get("original_name", ""))[:140],
            "status": status,
            "review_status": review_status[:40],
        })
        if status != "verified" and len(warnings) < MAX_WARNINGS:
            warnings.append({"code": status, "file_id": fid})
    selected_claims = [
        row for row in read_claims()[:1500]
        if str(row.get("file_id", "")) in selected
    ]
    validated = verified_selected_claim_ids(selected)
    unsupported = len(selected_claims) - sum(
        str(row.get("claim_id", "")) in validated for row in selected_claims
    )
    if unsupported:
        warnings.append({
            "code": "unsupported_selected_claims",
            "count": str(unsupported),
        })
    not_scanned = max(0, len(selected_rows) - len(inspected))
    if not_scanned:
        warnings.append({"code": "preview_not_all_sources_scanned",
                         "count": str(not_scanned)})
    return {
        "scope": "explicitly_selected_sources_only",
        "selected_documents": len(selected_rows),
        "inspected_originals": len(inspected),
        "verified_originals": counts.get("verified", 0),
        "originals_needing_attention": len(inspected) - counts.get("verified", 0),
        "not_scanned": not_scanned,
        "manual_review_pending_in_scan": counts.get("manual_review_pending", 0),
        "claims_in_selection": len(selected_claims),
        "claims_quote_verified": len(selected_claims) - unsupported,
        "claims_excluded_unverifiable": unsupported,
        "included_timeline_entries": sum(
            _within_selection(row, selected) for row in read_timeline_rows()
        ),
        "included_entities": sum(
            _within_selection(row, selected) for row in read_entity_rows()
        ),
        "included_tasks": sum(
            _within_selection(row, selected) for row in read_tasks()
        ),
        "selected_source_samples": per_source[:30],
        "sample_truncated": len(per_source) > 30,
        "warnings": warnings[:MAX_WARNINGS],
        "warning_list_truncated": len(warnings) > MAX_WARNINGS,
        "complete_preview": not not_scanned,
        "export_blocked_in_scanned_sources": any(
            item["status"] != "verified" for item in per_source
        ),
        "limits": {
            "preview_is_not_an_export_or_full_legal_assessment": True,
            "originals_are_checked_again_during_actual_export": True,
            "mixed_source_free_text_is_excluded": True,
            "unverified_claims_are_excluded_from_handoff": True,
            "no_external_data_completeness_claim": True,
        },
    }
