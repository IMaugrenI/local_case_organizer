"""Conservative source-grounded document-type hints, never verified classifications.

Filename labels and bounded, hash-verified local text are the only signals.
No machine learning, personal-identity guesses or legal conclusions.
"""
from __future__ import annotations

import re

from local_case_organizer.document_text import get_indexed
from local_case_organizer.register.store import read_register_rows

_MAX_DOCS = 80
_KINDS = (
    ("court", "Gerichtliche Unterlagen", "Court document",
     (r"urteil", r"beschluss", r"gericht", r"aktenzeichen", r"lad[uo]ng", r"protokoll")),
    ("enforcement", "Vollstreckung / Pfändung", "Enforcement / garnishment",
     (r"vollstreck", r"pf.ndung", r"gerichtsvollzieher", r"forderungspf.ndung")),
    ("employment", "Beschäftigung / Arbeitsverhältnis", "Employment",
     (r"arbeitsvertrag", r"lohnabrechnung", r"arbeitszeugnis", r"besch.ftigung")),
    ("correspondence", "Nachrichten und Schriftverkehr", "Correspondence",
     (r"e.?mail", r"whatsapp", r"schriftverkehr", r"brief", r"nachricht")),
    ("contracts", "Verträge und Vereinbarungen", "Contracts / agreements",
     (r"vertrag", r"vereinbarung", r"k.ndigung", r"unterschrift")),
    ("financial", "Zahlungen und Rechnungen", "Payments / invoices",
     (r"rechnung", r"kontoauszug", r"zahlung", r"quittung", r"forderung")),
)


def _match(sample: str) -> tuple[str, str, str] | None:
    for code, de, en, patterns in _KINDS:
        if any(re.search(pattern, sample, re.IGNORECASE) for pattern in patterns):
            return code, de, en
    return None


def document_type_hints() -> dict[str, object]:
    """Suggest type names with disclosed evidence source, never mutate register."""
    rows = read_register_rows()
    hints: list[dict[str, str]] = []
    unknown = 0
    for row in rows[:_MAX_DOCS]:
        file_id = str(row.get("file_id", ""))
        filename = str(row.get("original_name", ""))[:200]
        if not file_id:
            continue
        match = _match(filename)
        evidence = "filename_keyword" if match else ""
        if not match:
            try:
                indexed = get_indexed(file_id, verify_original=True)
                text = " ".join(str(page.get("text", ""))[:1200]
                                for page in indexed["pages"][:2])
                match = _match(text)
                evidence = "verified_local_index_keyword" if match else ""
            except (OSError, ValueError, TypeError):
                pass
        if match:
            code, label_de, label_en = match
            hints.append({
                "file_id": file_id,
                "original_name": filename,
                "type_code": code,
                "label_de": label_de,
                "label_en": label_en,
                "evidence_source": evidence,
                "status": "suggested_unverified",
            })
        else:
            unknown += 1
    return {
        "hints": hints[:_MAX_DOCS], "unknown_in_scan": unknown,
        "scanned": min(len(rows), _MAX_DOCS),
        "not_scanned": max(0, len(rows) - _MAX_DOCS),
        "note": "Labels are weak search aids, never confirmed document types",
    }
