"""Read-only, source-bound chronology and lawyer-facing case work summary.

This is an organizational overview, not a reconstructed legal truth.
Automated dates are verbatim source mentions; manual records are attributed to
the operator; differences require explicitly grouped and currently verifiable
quoted claims. There are no model calls, new evidence records or exports here.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from local_case_organizer.claims import read_claims
from local_case_organizer.comparison import comparison_report
from local_case_organizer.document_text import get_indexed
from local_case_organizer.entities.store import read_entity_rows
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.timeline.store import read_timeline_rows
from local_case_organizer.timeline.suggestions import propose_events

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MAX_DATES = 80
_MAX_PEOPLE = 60
_MAX_DISCREPANCIES = 20
_MAX_QUESTIONS = 9


def _links(value: object) -> set[str]:
    return {fid.strip() for fid in str(value or "").split(",") if fid.strip()}


def _valid_date(value: str) -> bool:
    if not _DATE.fullmatch(value):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _short(value: object, limit: int = 200) -> str:
    return " ".join(str(value or "").split())[:limit]


def _quote_supported(claim: dict[str, str], cache: dict[str, dict | None]) -> bool:
    fid = str(claim.get("file_id", ""))
    if fid not in cache:
        try:
            cache[fid] = get_indexed(fid, verify_original=True)
        except (ValueError, OSError, TypeError):
            cache[fid] = None
    index = cache[fid]
    if not index:
        return False
    quote = str(claim.get("source_quote", "")).strip()
    page_id = str(claim.get("source_page", ""))
    return bool(quote) and any(
        str(page.get("page")) == page_id and quote in str(page.get("text", ""))
        for page in index["pages"]
    )


def case_narrative(selected_ids: set[str] | None = None) -> dict[str, object]:
    """Return a bounded, case-scoped working overview without writing data.

    When selected_ids is supplied, *every* returned sensitive item is limited
    to fully linked, explicitly selected documents. Mixed-link manual entries
    are excluded rather than accidentally leaking their other context.
    """
    if selected_ids is not None and (
        not isinstance(selected_ids, set)
        or any(not isinstance(fid, str) for fid in selected_ids)
    ):
        raise ValueError("Selected source IDs must form a set of strings")
    register = read_register_rows()
    known = {str(row.get("file_id", "")) for row in register if row.get("file_id")}
    scope = known if selected_ids is None else known.intersection(selected_ids)
    names = {str(row.get("file_id")): _short(row.get("original_name"), 140)
             for row in register if str(row.get("file_id", "")) in scope}
    relevant = [row for row in register if str(row.get("file_id", "")) in scope]
    timeline: list[dict[str, object]] = []
    manual_total = 0
    for row in read_timeline_rows():
        linked = _links(row.get("linked_file_ids", ""))
        if not linked or not linked.issubset(scope):
            continue
        when = str(row.get("event_date", ""))
        if not _valid_date(when):
            continue
        manual_total += 1
        timeline.append({
            "date": when, "title": _short(row.get("event_title"), 160),
            "excerpt": _short(row.get("summary"), 190),
            "file_ids": sorted(linked),
            "source_kind": "operator_entered_not_verified",
            "review_status": _short(row.get("status") or "draft", 40),
            "page": None, "line": None,
            "event_id": _short(row.get("event_id"), 110),
        })

    # Reuse existing source-hash verification and exact page/line references.
    # Never promote a date mention to a recorded event automatically.
    suggestions = propose_events() if scope else {"candidates": [], "warnings": []}
    included_events = {str(row.get("event_id", "")) for row in read_timeline_rows()}
    for row in suggestions["candidates"]:
        fid = str(row.get("file_id", ""))
        when = str(row.get("date", ""))
        if fid not in scope or not _valid_date(when):
            continue
        if "EV-SUG-" + str(row.get("candidate_id", "")) in included_events:
            continue
        timeline.append({
            "date": when, "title": "Datumsnennung in einer Quelle",
            "excerpt": _short(row.get("excerpt"), 190),
            "file_ids": [fid],
            "source_kind": "verified_source_date_mention_not_an_event",
            "review_status": "suggested_not_verified",
            "page": int(row.get("page") or 1),
            "line": int(row.get("line") or 1),
            "event_id": str(row.get("candidate_id", "")),
        })
    timeline.sort(key=lambda row: (str(row["date"]), str(row["source_kind"]),
                                   str(row["file_ids"]), str(row["event_id"])))
    timeline_total = len(timeline)

    participants: list[dict[str, object]] = []
    for row in read_entity_rows():
        linked = _links(row.get("linked_file_ids", ""))
        if not linked or not linked.issubset(scope):
            continue
        participants.append({
            "name": _short(row.get("entity_name"), 160),
            "role": _short(row.get("entity_type"), 90),
            "file_ids": sorted(linked),
            "source_kind": "operator_entered_not_verified",
            "notes": _short(row.get("notes"), 190),
        })
        if len(participants) >= _MAX_PEOPLE:
            break

    # Comparison mismatches are human-created topical groupings. Revalidate
    # both quoted originals and keep at least two DIFFERENT sources and values.
    claims = {str(row.get("claim_id", "")): row for row in read_claims()}
    verified: dict[str, dict | None] = {}
    differences: list[dict[str, object]] = []
    for group in comparison_report()["review_candidates"]:
        sources = []
        for item in group.get("sources", []):
            fid = str(item.get("file_id", ""))
            claim = claims.get(str(item.get("claim_id", "")))
            if fid not in scope or not claim or claim.get("file_id") != fid:
                continue
            if not _quote_supported(claim, verified):
                continue
            sources.append({
                "file_id": fid,
                "page": int(claim.get("source_page") or 1),
                "quote": _short(claim.get("source_quote"), 240),
                "value": _short(item.get("value"), 120),
                "normalized": _short(item.get("normalized"), 120),
                "review_status": _short(claim.get("review_status") or "draft", 40),
            })
        if len({s["file_id"] for s in sources}) < 2:
            continue
        if len({s["normalized"] for s in sources}) < 2:
            continue
        differences.append({
            "topic": _short(group.get("topic"), 100),
            "kind": _short(group.get("kind"), 30),
            "sources": sources[:10],
            "status": "potential_difference_needs_human_review",
            "basis": "operator_grouped_source_verified_quotes",
        })
        if len(differences) >= _MAX_DISCREPANCIES:
            break

    questions: list[dict[str, str]] = []
    def question(code: str, text: str, hint: str) -> None:
        if len(questions) < _MAX_QUESTIONS:
            questions.append({"code": code, "text": text, "basis": hint})

    unreviewed = sum(
        1 for row in relevant if str(row.get("review_status", "unreviewed"))
        not in {"reviewed", "selected_for_export"}
    )
    if unreviewed:
        question("document_review", "Welche Unterlagen sind für den konkreten Fall relevant und geprüft?",
                 f"{unreviewed} Dokument(e) ohne abgeschlossenen Prüfstatus")
    suggested_dates = sum(1 for row in timeline if row["source_kind"].startswith("verified_source"))
    if suggested_dates:
        question("date_context", "Welche gefundenen Daten bezeichnen tatsächlich ein Ereignis und welche nur eine Erwähnung?",
                 f"{suggested_dates} unbestätigte Datumsnennung(en)")
    if manual_total:
        question("manual_events", "Sind die manuell erfassten Ereignisse durch ihre Originalquellen belegt?",
                 f"{manual_total} erfasste(r) Eintrag/Einträge")
    if differences:
        question("value_differences", "Wie erklären sich die unterschiedlich angegebenen Werte zu demselben manuell zugeordneten Thema?",
                 f"{len(differences)} mögliche(r) Abweichung(en) in quellengebundenen Aussagen")
    if not participants and relevant:
        question("participants", "Welche Personen und Organisationen sind beteiligt und welche Dokumente belegen ihre Rolle?",
                 "Keine manuell quellenverknüpften Beteiligten vorhanden")
    if relevant and len(relevant) > len({fid for row in timeline for fid in row["file_ids"]}):
        question("timeline_gaps", "Welche Unterlagen fehlen noch in einer nachvollziehbaren Chronologie?",
                 "Ein Teil der Unterlagen hat keinen zugeordneten chronologischen Eintrag")
    question("lawyer_review", "Welche Aussagen sind Dokumenteninhalt, Parteivortrag oder bereits rechtlich festgestellt?",
             "Eine rechtliche Bewertung wird nicht automatisch vorgenommen")

    return {
        "scope": "selected_originals_only" if selected_ids is not None else "active_case",
        "counts": {
            "documents": len(relevant), "chronology_items": timeline_total,
            "date_mentions_unverified": suggested_dates,
            "operator_events": manual_total, "participants": len(participants),
            "potential_value_differences": len(differences),
            "open_questions": len(questions),
        },
        "chronology": timeline[:_MAX_DATES],
        "participants": participants,
        "potential_differences": differences,
        "open_questions": questions,
        "source_names": names,
        "limits": {
            "chronology_max": _MAX_DATES,
            "verified_date_scan_limited": True,
            "event_truth_not_determined": True,
            "legal_deadlines_not_calculated": True,
            "claims_never_auto_approved": True,
            "unlinked_manual_records_excluded": True,
        },
    }


def _md(value: object, limit: int = 350) -> str:
    """Prevent Markdown structure/links or control text from untrusted source names."""
    clean = _short(value, limit)
    return re.sub(r"([\\`*_\[\]<>|#])", r"\\\1", clean)


def write_case_narrative(export_dir: Path, selected_ids: set[str]) -> Path:
    """Write the same read-only overview, strictly scoped to selected originals."""
    result = case_narrative(selected_ids)
    lines = [
        "# Sachverhaltsübersicht – ungeprüfter Arbeitsstand", "",
        "Automatisch zusammengestellt. Keine Rechtsberatung und keine verbindliche",
        "Sachverhaltsfeststellung. Jeder Eintrag muss mit der Originalquelle geprüft werden.", "",
        f"Ausgewählte Dokumente: {result['counts']['documents']}", "",
        "## Chronologischer Arbeitsstand", "",
    ]
    if not result["chronology"]:
        lines.append("- Keine quellenbezogenen Datums- oder Ereigniseinträge.")
    for row in result["chronology"]:
        refs = ", ".join(_md(x, 110) for x in row["file_ids"])
        place = (" · S. " + str(row["page"]) + ", Zeile " + str(row["line"])
                 if row["page"] is not None else "")
        kind = ("Datumsnennung, kein bestätigtes Ereignis"
                if row["source_kind"] == "verified_source_date_mention_not_an_event"
                else "manueller Eintrag, nicht automatisch verifiziert")
        lines.append("- " + _md(row["date"], 12) + " – " + _md(row["title"], 160)
                     + " (" + kind + "; Quelle: " + refs + place + ")")
        if row["excerpt"]:
            lines.append("  - Wortlaut / Arbeitsnotiz: " + _md(row["excerpt"], 190))
    lines.extend(["", "## Manuell erfasste Beteiligte – Rollen ungeprüft", ""])
    if not result["participants"]:
        lines.append("- Keine quellenverknüpften Beteiligten vorhanden.")
    for row in result["participants"]:
        lines.append("- " + _md(row["name"], 160) + " · " + _md(row["role"], 90)
                     + " (Quellen: " + ", ".join(_md(x, 110) for x in row["file_ids"]) + ")")
    lines.extend(["", "## Mögliche Wertabweichungen – keine bewiesenen Widersprüche", ""])
    if not result["potential_differences"]:
        lines.append("- Keine quellenverifizierten, manuell gruppierten Wertabweichungen festgestellt.")
    for group in result["potential_differences"]:
        lines.append("- Thema: " + _md(group["topic"], 100) + " (" + _md(group["kind"], 30) + ")")
        for src in group["sources"]:
            lines.append("  - " + _md(src["file_id"], 110) + ", Seite "
                         + str(src["page"]) + ": " + _md(src["value"], 120)
                         + " – Zitat: " + _md(src["quote"], 240))
    lines.extend(["", "## Offene Fragen für die fachliche Prüfung", ""])
    for row in result["open_questions"]:
        lines.append("- " + _md(row["text"], 220) + " (" + _md(row["basis"], 180) + ")")
    lines.extend(["", "## Nachweis- und Datenschutzgrenzen", "",
        "- Es wurden nur ausdrücklich ausgewählte Quell-IDs berücksichtigt.",
        "- Gemischt verknüpfte manuelle Einträge sind bei Teilübergaben ausgeschlossen.",
        "- Unbestätigte Datumsnennungen sind keine Ereignisfeststellungen.",
        "- Mögliche Abweichungen sind manuell gruppierte Quellenangaben, keine bewiesenen Widersprüche.",
        "- Keine automatische Fristberechnung, Quellenfreigabe, KI-Wahrheitsprüfung oder Versendung.",
        "- Die Übersicht kann begrenzt sein; fehlende Einträge beweisen nicht die Vollständigkeit.", "",
    ])
    target = export_dir / "SACHVERHALT_ARBEITSSTAND.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target
