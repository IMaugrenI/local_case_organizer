"""Selected-only, source-linked handoff metadata and neutral lawyer reading guide.

This intentionally does not perform legal reasoning, pick documents,
communicate with counsel, or infer contradictions and missing evidence.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from local_case_organizer.claims import read_claims
from local_case_organizer.export.quality import _within_selection, verified_selected_claim_ids
from local_case_organizer.entities.store import read_entity_rows
from local_case_organizer.paths import get_workspace_paths
from local_case_organizer.timeline.suggestions import propose_events
from local_case_organizer.ui.document_triage import document_type_hints
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.tasks import read_tasks
from local_case_organizer.timeline.store import read_timeline_rows


def _linked(value: object, selection: set[str]) -> list[str]:
    return [s.strip() for s in str(value or "").split(",")
            if s.strip() in selection]


def _safe(value: object, limit: int = 500) -> str:
    raw = " ".join(str(value or "").split())[:limit]
    # Escape MD syntax and terminal-like sequences in untrusted user material.
    return re.sub(r"([\\\x60*_\[\]<>|])", r"\\\1", raw)


def _csv_safe(value: object) -> str:
    cell = str(value or "")
    return "'" + cell if cell.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else cell


def write_selected_tables(export_dir: Path, selection: set[str]) -> list[str]:
    """Export only selected-source rows and remove references to other IDs."""
    valid_claims = verified_selected_claim_ids(selection)
    definitions = (
        ("document_register.csv", read_register_rows(), "file_id"),
        ("timeline.csv", read_timeline_rows(), "linked_file_ids"),
        ("claims.csv", read_claims(), "file_id"),
        ("entities.csv", read_entity_rows(), "linked_file_ids"),
        ("tasks.csv", read_tasks(), "linked_file_ids"),
    )
    exported: list[str] = []
    for filename, source_rows, key in definitions:
        included = []
        for source in source_rows:
            if key == "linked_file_ids":
                if not _within_selection(source, selection):
                    continue
                row = dict(source)
            else:
                if str(source.get(key, "")) not in selection:
                    continue
                if filename == "claims.csv" and str(source.get("claim_id", "")) not in valid_claims:
                    continue
                row = dict(source)
            included.append(row)
        # Omit tables with no linked entries; no unrelated metadata escapes.
        if not included:
            continue
        fields = list(included[0].keys())
        dest = export_dir / filename
        with dest.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in included:
                writer.writerow({col: _csv_safe(row.get(col, "")) for col in fields})
        exported.append(filename)
    return exported


def write_lawyer_start_here(export_dir: Path, selection: set[str]) -> Path:
    """Write a one-page reading guide grounded only in selected file IDs."""
    rows = [row for row in read_register_rows() if row.get("file_id") in selection]
    events = [event for event in read_timeline_rows()
              if _within_selection(event, selection)]
    valid_claims = verified_selected_claim_ids(selection)
    claims = [row for row in read_claims() if row.get("file_id") in selection
              and str(row.get("claim_id", "")) in valid_claims]
    people = [row for row in read_entity_rows()
              if _within_selection(row, selection)]
    unreviewed = sum(str(row.get("review_status", "")) not in
                     {"reviewed", "selected_for_export"} for row in rows)
    lines = [
        "# Anwalt: Einstieg in diese Fallakte", "",
        "Automatisch strukturierte Arbeitsübersicht. Keine Rechtsberatung, keine",
        "automatische Wahrheitsprüfung und keine Aussage über den Verfahrensstand.", "",
        "## Umfang dieser Übergabe", "",
        f"- Ausdrücklich ausgewählte Originaldateien: {len(rows)}",
        f"- Zugeordnete Zeitleisteneinträge: {len(events)}",
        f"- Manuell erfasste, quellenbezogene Aussagen: {len(claims)}",
        f"- Zugeordnete Personen/Organisationen: {len(people)}",
        f"- Dokumente ohne abgeschlossenen manuellen Prüfstatus: {unreviewed}", "",
        "## Lesereihenfolge", "",
        "1. EVIDENCE_INDEX.csv enthält Dateinamen, Dokument-IDs und SHA-256-Prüfsummen.",
        "2. selected_originals/ enthält ausschließlich die ausgewählten Anlagen.",
        "3. SACHVERHALT_ARBEITSSTAND.md enthält die geordnete, ungeprüfte Sachverhaltsübersicht.",
        "4. DOSSIER.md enthält die dokumentierten Ereignisse und wörtlichen Quellenzitate.",
        "5. Die CSV-Dateien sind nach den ausgewählten Quell-IDs gefilterte Arbeitsdaten.", "",
        "## Anlagenverzeichnis", "",
    ]
    for row in rows[:300]:
        fid = _safe(row.get("file_id"), 110)
        name = _safe(row.get("original_name"), 170)
        status = _safe(row.get("review_status") or "unreviewed", 30)
        lines.append(f"- {fid}: {name} (Prüfstatus: {status})")
    lines.extend(["", "## Erfasste zeitliche Angaben (Arbeitsentwürfe)", ""])
    if not events:
        lines.append("- Keine ausgewählten Quellen zugeordneten Einträge.")
    for event in sorted(events, key=lambda row: str(row.get("event_date", "")))[:100]:
        refs = ",".join(_linked(event.get("linked_file_ids"), selection))
        lines.append("- " + _safe(event.get("event_date") or "ohne Datum", 25)
                     + " — " + _safe(event.get("event_title"), 160)
                     + " (Quellen: " + _safe(refs, 180) + "; "
                     + _safe(event.get("status") or "draft", 30) + ")")
    # Optional, source-bound search aids. Never promote unreviewed hints
    # into the curated event timeline or legal conclusions.
    guesses = [hint for hint in document_type_hints()["hints"]
               if hint["file_id"] in selection][:60]
    lines.extend(["", "## Automatisch vorgeschlagene Dokumentarten (nicht geprüft)", ""])
    if not guesses:
        lines.append("- Keine belastbaren Stichwort-Hinweise in den ausgewählten Dateien.")
    for guess in guesses:
        lines.append("- " + _safe(guess["file_id"], 110) + ": "
                     + _safe(guess["label_de"], 90)
                     + " (Suchhilfe aus " + _safe(guess["evidence_source"], 40) + ")")
    date_hints = [item for item in propose_events()["candidates"]
                  if item["file_id"] in selection][:35]
    lines.extend(["", "## Automatisch gefundene Datumsstellen (unbestätigt)", ""])
    if not date_hints:
        lines.append("- Keine passenden Fundstellen in den geeigneten ausgewählten Quellen.")
    for item in date_hints:
        lines.append("- " + _safe(item["date"], 12) + " · "
                     + _safe(item["file_id"], 110) + " · Seite "
                     + str(int(item.get("page", 1))) + ", Zeile "
                     + str(int(item["line"])) + ": "
                     + _safe(item["excerpt"], 200))
    lines.extend(["", "## Vom Anwalt bzw. Betreiber zu prüfen", "",
        "- Welche Unterlagen sind für die konkrete Frage oder das Verfahren relevant?",
        "- Stimmen die Datumsangaben mit den Originalen und dem Aktenstand überein?",
        "- Welche Aussagen sind Parteivortrag, welche Dokumenteninhalt, welche bereits festgestellt?",
        "- Welche weiteren Belege oder Verfahrensunterlagen fehlen?",
        "- Sind die vom Betreiber eingetragenen Termine korrekt? Keine Fristenberechnung.", "",
        "## Grenzen und Datenschutz", "",
        "- Nur ausdrücklich ausgewählte Originale und ausschließlich mit ihnen verknüpfte Datensätze sind enthalten.",
        "- Gemischte Einträge mit ausgeschlossenen Quellen werden vollständig zurückgehalten.",
        "- Nicht mehr original- und zitatgeprüfte Aussagen sind ausgeschlossen.",
        "- Nicht ausgewählte Aktenbestandteile sind bewusst ausgeschlossen.",
        "- Datums- und Wertabweichungen sind höchstens Prüfanlässe, kein Widerspruchsbeweis.",
        "- Das Paket wurde lokal erstellt und nicht automatisch versendet.",
        "- Vollständigkeit und rechtliche Relevanz müssen fachlich geprüft werden.", "",
    ])
    dest = export_dir / "ANWALT_START_HERE.md"
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest
