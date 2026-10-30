"""A15: Selected-only neutral handoff quality reading note."""
from __future__ import annotations

import re
from pathlib import Path


def _md(value: object, limit: int = 160) -> str:
    clean = " ".join(str(value or "").split())[:limit]
    return re.sub(r"([\\`*_\[\]<>|#])", r"\\\1", clean)


def write_quality_report(export_dir: Path, preview: dict[str, object]) -> Path:
    """Write only selected identifiers; this is not an audit certification."""
    lines = [
        "# Übergabeprüfung – organisatorischer Arbeitsstand", "",
        "Dieser Bericht bezieht sich ausschließlich auf ausgewählte Quellen.",
        "Er bestätigt weder Aktenvollständigkeit noch Tatsachen, Recht oder Beweiswert.", "",
        "## Umfang der ausgewählten Anlagen", "",
        f"- Ausgewählte Originaldokumente: {int(preview['selected_documents'])}",
        f"- Im Vorschaufenster auf Hash geprüft: {int(preview['inspected_originals'])}",
        f"- Dabei unveränderte Originale: {int(preview['verified_originals'])}",
        f"- Nicht gescannte Quellen: {int(preview['not_scanned'])}",
        f"- Dokumente im Scan mit offenem manuellem Prüfstatus: {int(preview['manual_review_pending_in_scan'])}",
        f"- Quellengebundene Aussagen in Auswahl: {int(preview['claims_in_selection'])}",
        f"- Mit Original und Seitenzitat verifizierbare Aussagen: {int(preview['claims_quote_verified'])}",
        f"- Aus dem Export ausgeschlossene nicht verifizierbare Aussagen: {int(preview['claims_excluded_unverifiable'])}",
        f"- Ausschließlich den gewählten Quellen zugeordnete Zeitlinieneinträge: {int(preview['included_timeline_entries'])}",
        f"- Ausschließlich den gewählten Quellen zugeordnete Beteiligteneinträge: {int(preview['included_entities'])}",
        f"- Ausschließlich den gewählten Quellen zugeordnete Aufgaben: {int(preview['included_tasks'])}", "",
        "## Prüfhinweise zu ausgewählten Quellen", "",
    ]
    for warning in preview["warnings"]:
        code = _md(warning.get("code", ""), 70)
        fid = _md(warning.get("file_id", ""), 110)
        count = _md(warning.get("count", ""), 30)
        lines.append(f"- {code}" + (f" · Datei-ID: {fid}" if fid else "") +
                     (f" · Anzahl: {count}" if count else ""))
    if not preview["warnings"]:
        lines.append("- Keine gescannten Warnhinweise; die Aussage ist ausdrücklich auf diesen Scan begrenzt.")
    lines.extend([
        "", "## Grenzen der Übergabe", "",
        "- Das Prüffenster scannt höchstens 120 ausgewählte Originale.",
        "- Die Originale werden beim tatsächlichen Kopieren nochmals hashgeprüft.",
        "- Ein vorhandener Hash sagt nichts über den Wahrheitsgehalt des Inhalts.",
        "- Ein fehlender Textindex bedeutet nicht, dass die Originaldatei fehlt.",
        "- Manuelle Einträge mit Referenzen auf ausgeschlossene Quellen werden vollständig ausgelassen.",
        "- Quellenzitate ohne aktuelle Original- und Seitenprüfung gelangen nicht in die Quellen-Aussagen-Tabellen.",
        "- Die Weitergabe des ZIP-Pakets ist eine separate Betreiberentscheidung.",
        "- Die reale Aktenvollständigkeit muss der Empfänger selbst prüfen.", "",
    ])
    dest = export_dir / "UEBERGABE_PRUEFPUNKTE.md"
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest
