"""Explainable document relationships from exact labels in hash-verified sources.

This does not assert a shared proceeding or event as fact. A matching explicitly
labelled case reference is solely a review hint. Everything is read-only and
restricted to the selected case or explicitly selected export documents.
"""
from __future__ import annotations

import re
import unicodedata

from local_case_organizer.document_text import get_indexed
from local_case_organizer.register.store import read_register_rows

MAX_SCANNED = 120
MAX_GROUPS = 24
MAX_PAGES = 3
MAX_CHARS_PER_PAGE = 6500

_REF = re.compile(
    r"(?im)^[ \t]*(?P<label>Aktenzeichen|Az\.?|Geschäftszeichen|"
    r"Gesch\.?-?Z\.?|Case[ \t]*(?:number|no\.?)|File[ \t]*no\.?|"
    r"Vorgangsnummer|Fallnummer|Mandatsnummer|Vertragsnummer|"
    r"Rechnungsnummer|Schadennummer)"
    r"[ \t]*[:#]?[ \t]+(?P<value>[^\r\n]{4,85})[ \t]*$"
)
_SPACES = re.compile(r"\s+")


def _reference_kind(label: str) -> tuple[str, str]:
    """Disjoint categories prevent accidental cross-type ID collisions."""
    label = unicodedata.normalize("NFKC", label).casefold().strip(". :")
    if label.startswith(("aktenzeichen", "az", "geschäftszeichen", "gesch", "case", "file")):
        return "case", "Aktenzeichen"
    if label.startswith(("vorgang", "fall", "mandat")):
        return "matter", "Vorgangsnummer"
    if label.startswith("vertrag"):
        return "contract", "Vertragsnummer"
    if label.startswith("rechnung"):
        return "invoice", "Rechnungsnummer"
    return "claim", "Schadennummer"


def _normalized_ref(value: str) -> str | None:
    """Accept only unambiguous, sufficiently specific explicit references."""
    value = unicodedata.normalize("NFKC", value).strip().strip(" .,:;")
    value = _SPACES.sub(" ", value)
    if not 5 <= len(value) <= 65 or len(re.findall(r"\d", value)) < 2:
        return None
    if any(ord(c) < 32 for c in value):
        return None
    # Casefold and whitespace normalization only; never guess which
    # differently written case numbers are the same.
    return value.casefold()


def linked_document_hints(selected_ids: set[str] | None = None) -> dict[str, object]:
    """Group multiple verified originals with the same explicit case reference.

    A selection supplied by the export path is enforced before any text is read,
    including the returned filename, quotation and counts.
    """
    if selected_ids is not None and (
        not isinstance(selected_ids, set)
        or any(not isinstance(fid, str) for fid in selected_ids)
    ):
        raise ValueError("Source selection must be a set of IDs")
    rows = read_register_rows()
    scope = {
        str(row.get("file_id")): str(row.get("original_name", ""))[:140]
        for row in rows if row.get("file_id") and (
            selected_ids is None or str(row["file_id"]) in selected_ids
        )
    }
    scanned = 0
    available = 0
    occurrences: dict[tuple[str, str], list[dict[str, object]]] = {}
    for file_id in list(scope)[:MAX_SCANNED]:
        scanned += 1
        try:
            indexed = get_indexed(file_id, verify_original=True)
        except (ValueError, OSError, TypeError):
            continue
        available += 1
        seen_in_doc: set[tuple[str, str]] = set()
        for page in indexed["pages"][:MAX_PAGES]:
            text = str(page.get("text", ""))[:MAX_CHARS_PER_PAGE]
            for match in _REF.finditer(text):
                reference = _normalized_ref(match.group("value"))
                if reference is None:
                    continue
                kind, label = _reference_kind(match.group("label"))
                key = (kind, reference)
                if key in seen_in_doc:
                    continue
                seen_in_doc.add(key)
                occurrences.setdefault(key, []).append({
                    "file_id": file_id,
                    "original_name": scope[file_id],
                    "page": int(page["page"]),
                    "source_quote": match.group(0).strip()[:140],
                })
                if len(seen_in_doc) >= 8:
                    break
            if len(seen_in_doc) >= 8:
                break
    groups: list[dict[str, object]] = []
    for (kind, ref), mentions in sorted(occurrences.items()):
        if len({str(m["file_id"]) for m in mentions}) < 2:
            continue
        label = {
            "case": "Aktenzeichen", "matter": "Vorgangsnummer",
            "contract": "Vertragsnummer", "invoice": "Rechnungsnummer",
            "claim": "Schadennummer",
        }[kind]
        groups.append({
            "reference": ref[:65],
            "reference_kind": kind, "reference_label": label,
            "documents": mentions[:25],
            "document_count": len(mentions),
            "match_basis": "exact_explicit_typed_reference_in_verified_local_text",
            "status": "possible_connection_requires_human_review",
        })
        if len(groups) >= MAX_GROUPS:
            break
    return {
        "groups": groups,
        "scanned": scanned,
        "verified_text_available": available,
        "unavailable_or_unindexed": scanned - available,
        "not_scanned": max(0, len(scope) - scanned),
        "incomplete": len(scope) > MAX_SCANNED or available < scanned,
        "limitations": {
            "identical_reference_does_not_establish_shared_proceeding": True,
            "reference_type_is_kept_separate": True,
            "no_unlabelled_or_fuzzy_matching": True,
            "no_automatic_entity_or_event_writes": True,
        },
    }
