"""Read-only, case-scoped briefing for long-running document-heavy proceedings.

Uses existing verified-source suggestion and manual-review stores. Counts and
potential review hints are NOT legal conclusions, contradictions or deadlines.
No background work, text leakage, source modifications or external transfers.
"""
from __future__ import annotations

from local_case_organizer.claims import read_claims
from local_case_organizer.ai_exchange import read_ai_suggestions
from local_case_organizer.document_text import get_indexed
from local_case_organizer.ui.document_triage import document_type_hints
from local_case_organizer.comparison import comparison_report
from local_case_organizer.entities.store import read_entity_rows
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.tasks import task_board
from local_case_organizer.timeline.store import read_timeline_rows
from local_case_organizer.timeline.suggestions import propose_events


def case_briefing() -> dict[str, object]:
    """Summarize evidence organization and human-review queues, without judging truth."""
    documents = read_register_rows()
    timeline = read_timeline_rows()
    entities = read_entity_rows()
    claims = read_claims()
    board = task_board()
    dates = propose_events() if documents else {"candidates": [], "warnings": []}
    comparisons = comparison_report() if claims else {"review_candidates": []}

    # AI suggestions are never facts; only show hints which still have a
    # hash-verified original and verbatim page quote. Keep startup bounded.
    ai_hints: list[dict[str, object]] = []
    verified_pages: dict[str, dict | None] = {}
    for item in read_ai_suggestions()[:32]:
        if item.get("status") != "pending_review":
            continue
        fid = str(item.get("file_id", ""))
        if fid not in verified_pages:
            try:
                verified_pages[fid] = get_indexed(fid, verify_original=True)
            except (ValueError, OSError):
                verified_pages[fid] = None
        indexed = verified_pages[fid]
        if not indexed:
            continue
        page = next((page for page in indexed["pages"]
                     if str(page.get("page")) == str(item.get("page"))), None)
        if not page or str(item.get("source_quote", "")) not in str(page["text"]):
            continue
        ai_hints.append({
            "suggestion_id": str(item.get("suggestion_id", "")),
            "file_id": fid, "page": str(item.get("page", "")),
            "source_quote": str(item.get("source_quote", ""))[:350],
            "statement": str(item.get("statement", ""))[:450],
            "status": "pending_review",
        })
    types = document_type_hints() if documents else {"hints": [], "unknown_in_scan": 0}

    recorded_dates = {str(row.get("event_id", "")) for row in timeline}
    candidates = [
        row for row in dates.get("candidates", [])
        if "EV-SUG-" + str(row.get("candidate_id", "")) not in recorded_dates
    ]
    tasks = [
        row for row in board["tasks"]
        if row.get("status") not in ("done", "cancelled")
    ]
    urgent = [
        row for row in tasks
        if row.get("date_indicator") in ("overdue", "due_today")
    ]
    undecided = [
        row for row in documents
        if str(row.get("review_status") or "unreviewed") in ("", "unreviewed", "flagged")
    ]
    issues = [
        row for row in comparisons.get("review_candidates", [])
        if row.get("status") == "potential_mismatch_needs_human_review"
    ]
    unlinked = [
        row for row in documents
        if row.get("file_id") and not any(
            str(row["file_id"]) in [
                x.strip() for x in str(linked.get("linked_file_ids", "")).split(",")
            ] for linked in (*timeline, *entities)
        )
    ]
    return {
        "totals": {
            "documents": len(documents),
            "review_pending": len(undecided),
            "timeline_entries": len(timeline),
            "date_suggestions": len(candidates),
            "open_tasks": len(tasks),
            "urgent_manual_dates": len(urgent),
            "potential_value_differences": len(issues),
            "unlinked_documents": len(unlinked),
            "unreviewed_ai_hints": len(ai_hints),
            "selected_export": sum(
                str(row.get("selected_for_export", "")).lower() == "yes"
                for row in documents
            ),
        },
        "next_actions": (
            ([{"kind": "manual_date", "count": len(urgent)}] if urgent else [])
            + ([{"kind": "review_documents", "count": len(undecided)}] if undecided else [])
            + ([{"kind": "review_dates", "count": len(candidates)}] if candidates else [])
            + ([{"kind": "review_ai", "count": len(ai_hints)}] if ai_hints else [])
            + ([{"kind": "review_comparisons", "count": len(issues)}] if issues else [])
            + ([{"kind": "organize_sources", "count": len(unlinked)}] if unlinked else [])
        )[:5],
        "ai_review_samples": ai_hints[:8],
        "date_samples": [
            {
                "candidate_id": str(row["candidate_id"]),
                "file_id": str(row["file_id"]),
                "date": str(row["date"]),
                "original_name": str(row["original_name"]),
                "line": row["line"],
                "page": row.get("page", 1),
                "excerpt": str(row["excerpt"]),
            }
            for row in candidates[:8]
        ],
        "urgent_tasks": [
            {
                "task_id": str(row.get("task_id", "")),
                "title": str(row.get("title", ""))[:180],
                "due_date": str(row.get("due_date", "")),
                "date_indicator": str(row.get("date_indicator", "")),
                "linked_file_ids": str(row.get("linked_file_ids", "")),
            } for row in urgent[:8]
        ],
        "comparison_samples": [
            {
                "topic": str(item.get("topic", "")),
                "kind": str(item.get("kind", "")),
                "sources": [
                    {"file_id": str(source.get("file_id", "")),
                     "claim_id": str(source.get("claim_id", "")),
                     "value": str(source.get("value", ""))}
                    for source in item.get("sources", [])[:8]
                ],
            }
            for item in issues[:5]
        ],
        "document_type_hints": types["hints"][:30],
        "document_types_unclassified": types["unknown_in_scan"],
        "limitations": {
            "date_mentions_are_unverified": True,
            "possible_comparisons_need_human_review": True,
            "task_dates_are_manually_entered_not_calculated_legal_deadlines": True,
            "analysis_limited_to_eligible_verified_text_files": True,
        },
    }
