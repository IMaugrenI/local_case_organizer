"""Neutral, source-linked, opt-in dossier additions for the existing export bundle."""
from __future__ import annotations

import csv
import html
from datetime import datetime
from pathlib import Path

from local_case_organizer.claims import read_claims
from local_case_organizer.export.helpers import load_provenance_index
from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.timeline.store import read_timeline_rows


def _text(value: object, length: int = 300) -> str:
    line = " ".join(str(value or "").split())[:length]
    return html.escape(line, quote=True).replace("|", "&#124;")


def _csv_value(value: object) -> str:
    line = " ".join(str(value or "").split())[:300]
    return "'" + line if line.lstrip().startswith(("=", "+", "-", "@")) else line


def _date_sort(row: dict) -> tuple:
    raw = str(row.get("event_date", ""))[:10]
    try:
        return (0, datetime.fromisoformat(raw).date().isoformat())
    except ValueError:
        return (1, str(row.get("event_id", "")))


def dossier_preview() -> dict:
    selected = {str(row.get("file_id", "")) for row in read_register_rows()
                if str(row.get("selected_for_export", "")).lower() == "yes"}
    return {
        "selected_documents": len(selected),
        "entered_timeline_rows": sum(bool(row.get("event_title")) for row in read_timeline_rows()),
        "claims_in_selection": sum(row.get("file_id") in selected for row in read_claims()),
        "note": "Counts are a preview. Source-integrity checks happen during export.",
    }


def write_dossier(export_dir: Path, selected_paths: list[str]) -> list[str]:
    """Only selected originals become attachments; preserve source IDs and hashes."""
    selected = [r for r in read_register_rows()
                if str(r.get("selected_for_export", "")).lower() == "yes"]
    if len(selected) != len(selected_paths) or len(selected) > 1200:
        raise ValueError("Selected file mapping is inconsistent or oversized")
    ids = [str(r.get("file_id", "")) for r in selected]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate selected document IDs")
    provenance = load_provenance_index(get_workspace_paths().register_dir)
    index = []
    for row, attachment in zip(selected, selected_paths):
        fid = str(row.get("file_id", ""))
        source = provenance.get(fid, {})
        sha = str(source.get("sha256", ""))
        if len(sha) != 64:
            raise ValueError("Selected attachment lacks SHA-256 provenance")
        index.append({
            "file_id": _csv_value(fid),
            "original_name": _csv_value(row.get("original_name", "")),
            "attachment": _csv_value(attachment),
            "sha256": sha,
            "review_status": _csv_value(row.get("review_status", "")),
        })
    index_path = export_dir / "EVIDENCE_INDEX.csv"
    with index_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream,
                                fieldnames=["file_id", "original_name", "attachment",
                                            "sha256", "review_status"])
        writer.writeheader()
        writer.writerows(index)
    lines = [
        "# Case dossier – neutral handoff", "",
        "This index summarizes case records without asserting factual or legal truth.", "",
        "## Selected original documents", "",
        f"{len(index)} selected attachment(s). The ZIP manifest contains file hashes.", "",
    ]
    for record in index:
        lines.append("- " + _text(record["file_id"]) + ": " +
                     _text(record["original_name"]) + " / " + _text(record["attachment"]) +
                     " / SHA-256: " + _text(record["sha256"]))
    lines.extend(["", "## Entered timeline", "",
                  "Dates and descriptions are unverified working entries.", ""])
    for event in sorted(read_timeline_rows(), key=_date_sort)[:1200]:
        if not str(event.get("event_title", "")).strip():
            continue
        refs = [s.strip() for s in str(event.get("linked_file_ids", "")).split(",")]
        bundled = [s for s in refs if s in ids]
        lines.append("- " + _text(event.get("event_date") or "undated") + " / " +
                     _text(event.get("event_title")) + " / status: " +
                     _text(event.get("status")) + " / included references: " +
                     _text(", ".join(bundled) or "none"))
    lines.extend(["", "## Quoted source claims", "",
                  "Reviewed status records operator review, not independent verification.", ""])
    for claim in read_claims()[:1500]:
        if claim.get("file_id") not in ids:
            continue
        lines.append("- " + _text(claim.get("claim_id")) + " / document " +
                     _text(claim.get("file_id")) + " / page " +
                     _text(claim.get("source_page")) + " / " +
                     _text(claim.get("review_status")))
        lines.append("  - Source quote: " + _text(claim.get("source_quote"), 500))
        lines.append("  - Claim: " + _text(claim.get("statement"), 600))
    lines.extend(["", "## Limitations", "",
                  "- Selected originals were checked against provenance before export.",
                  "- Source statements are not proof of legal or factual conclusions.",
                  "- Unselected originals are not included as attachments.",
                  "- Review the export_manifest.json and ZIP checksum.",
                  ""])
    (export_dir / "DOSSIER.md").write_text("\n".join(lines), encoding="utf-8")
    return ["DOSSIER.md", "EVIDENCE_INDEX.csv"]
