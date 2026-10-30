"""A14: Explicit review work items on the existing audited case task board.

No review outcome, factual/legal assertion, export approval, model operation or
deadline is inferred from a task. The review queue is a bounded snapshot. Source
changes are surfaced without modifying the task or the underlying evidence.
"""
from __future__ import annotations

import hashlib
import json
import re

from local_case_organizer.tasks import add_review_task, read_tasks
from local_case_organizer.export.helpers import load_provenance_index
from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.ui.case_coverage import _source_status
from local_case_organizer.ui.case_briefing import case_briefing
from local_case_organizer.ui.case_narrative import case_narrative
from local_case_organizer.ui.connection_review import reviewed_document_hints

_KIND = {"document", "claim", "connection", "question"}
_MAX_PER_KIND = 20
_REVIEW_ID = re.compile(r"[a-zA-Z0-9_-]{1,110}\Z")


def _token(kind: str, ref: str, status: str, sources: list[str],
           evidence: str) -> str:
    value = [kind, ref, status, sorted(sources), evidence]
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _candidates() -> list[dict[str, object]]:
    briefing = case_briefing()["review_queue"]
    narrative = case_narrative()
    links = {
        group["group_id"]: group for group in reviewed_document_hints()["groups"]
        if group["status"] in {"pending_review", "recheck_required"}
    }
    suggestions: list[dict[str, object]] = []
    paths = get_workspace_paths()
    doc_rows = {str(row.get("file_id", "")): row for row in read_register_rows()}
    provenance = load_provenance_index(paths.register_dir)

    for row in briefing["document_samples"][:_MAX_PER_KIND]:
        fid = str(row["file_id"])
        status = str(row["review_status"])
        title = "Dokument organisatorisch prüfen: " + str(row["original_name"])[:100]
        document_row = doc_rows.get(fid)
        original_state = (_source_status(document_row, provenance, paths.originals_dir)
                          if document_row is not None else "unknown_document")
        suggestions.append({
            "kind": "document", "ref": fid, "status": "pending_review",
            "title": title[:180], "file_ids": [fid],
            "token": _token("document", fid, status, [fid],
                            str(row["original_name"]) + "|" + original_state),
            "note": "Dokumentstatus und Quelle im bestehenden Register manuell kontrollieren. Keine Tatsachenbestätigung.",
        })

    for row in briefing["claim_samples"][:_MAX_PER_KIND]:
        ref = str(row["claim_id"])
        fid = str(row["file_id"])
        status = str(row["status"])
        suggestions.append({
            "kind": "claim", "ref": ref, "status": status,
            "title": "Quellengebundene Aussage prüfen: " + ref,
            "file_ids": [fid], "token": _token(
                "claim", ref, status, [fid],
                str(row.get("source_page", "")) + "|" +
                str(row.get("source_quote", "")) + "|" +
                str(row.get("statement", "")),
            ),
            "note": ("Original oder Seitenzitat erneut prüfen; keine unbestätigten Texte übernehmen."
                     if status == "recheck_required"
                     else "Manuell feststellen, ob das Quellenzitat zur eingegebenen Aussage gehört. Keine Wahrheitsfreigabe."),
        })

    for row in briefing["connection_samples"][:_MAX_PER_KIND]:
        ref = str(row["group_id"])
        group = links.get(ref)
        if group is None:
            continue
        members = sorted({str(entry["file_id"]) for entry in group["documents"]})
        status = str(group["status"])
        title = "Dokumentbezug organisatorisch prüfen: " + str(group["reference"])[:110]
        suggestions.append({
            "kind": "connection", "ref": ref, "status": status,
            "title": title[:180],
            # Link references to existing task CSV (max 20), while group
            # signature still captures the *complete* original proposal.
            "file_ids": members[:20],
            "token": _token("connection", ref, status, members,
                            str(group["source_signature"])),
            "note": "Gleiche Referenz ist nur ein Sortierhinweis; fachlich prüfen, keine automatische Aktenzusammenführung.",
        })

    for row in narrative["open_questions"][:_MAX_PER_KIND]:
        ref = str(row["code"])
        title = str(row["text"])[:180]
        suggestions.append({
            "kind": "question", "ref": ref, "status": "open_question",
            "title": title, "file_ids": [],
            "token": _token("question", ref, "open_question", [], title + "|" + str(row["basis"])),
            "note": ("Offene organisatorische Frage aus der fallbezogenen Sachverhaltsübersicht. "
                     "Manuell klären, keine Rechtsprüfung durch die Software."),
        })
    return suggestions


def review_workflow() -> dict[str, object]:
    """Read-only review-to-task links including source-context drift hints."""
    candidates = _candidates()
    mapping = {(str(item["kind"]), str(item["ref"])): item for item in candidates}
    tasks = []
    for row in read_tasks():
        kind = str(row.get("review_kind", ""))
        ref = str(row.get("review_ref", ""))
        if kind not in _KIND or not _REVIEW_ID.fullmatch(ref):
            continue
        current = mapping.get((kind, ref))
        saved_token = str(row.get("review_token", ""))
        status = (
            "review_item_not_in_current_queue" if current is None
            else "review_context_changed" if saved_token != current["token"]
            else "review_context_current"
        )
        tasks.append({
            "task_id": str(row.get("task_id", "")),
            "kind": kind, "ref": ref, "task_status": str(row.get("status", "")),
            "source_status": status, "title": str(row.get("title", ""))[:180],
            "linked_file_ids": str(row.get("linked_file_ids", ""))[:800],
        })
    tasks.sort(key=lambda row: (row["task_status"] in {"done", "cancelled"},
                                row["kind"], row["ref"]))
    return {
        "candidates": [
            {key: item[key] for key in ("kind", "ref", "title", "token", "status")}
            for item in candidates
        ],
        "review_tasks": tasks[:60],
        "review_tasks_total": len(tasks),
        "review_tasks_not_displayed": max(0, len(tasks) - 60),
        "candidate_limit_per_kind": _MAX_PER_KIND,
        "limitations": {
            "task_completion_never_approves_review_or_original": True,
            "no_deadlines_or_reminders_are_generated": True,
            "missing_candidate_does_not_prove_resolution": True,
            "queue_is_bounded_and_may_be_incomplete": True,
            "local_case_only": True,
        },
    }


def create_task_for_review(kind: str, ref: str, token: str) -> dict[str, object]:
    """Explicit one-item request using a fresh server-side review snapshot."""
    if (kind not in _KIND or not isinstance(ref, str)
            or not _REVIEW_ID.fullmatch(ref)
            or not isinstance(token, str)
            or not re.fullmatch(r"[a-f0-9]{64}", token)):
        raise ValueError("Invalid review-task request")
    current = next(
        (item for item in _candidates()
         if item["kind"] == kind and item["ref"] == ref), None
    )
    if current is None or current["token"] != token:
        raise ValueError("Review item has changed, is not available, or no longer needs action")
    return add_review_task(
        title=str(current["title"]), review_kind=kind,
        review_ref=ref, review_token=token,
        linked_file_ids=",".join(current["file_ids"]),
        note=str(current["note"]),
    )
