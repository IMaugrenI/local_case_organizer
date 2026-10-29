"""Synthetic end-to-end checks for read-only case narrative and selected-only handoff."""
from __future__ import annotations

from zipfile import ZipFile

import pytest

from local_case_organizer import paths
from local_case_organizer.claims import add_claim
from local_case_organizer.comparison import add_comparison
from local_case_organizer.document_text import index_document
from local_case_organizer.entities.store import write_entity_rows
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.timeline.store import write_timeline_rows
from local_case_organizer.ui.case_narrative import case_narrative
from local_case_organizer.ui.quick_intake import quick_organize_inbox


def _case(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    (workspace.inbox_dir / "gericht_2020.txt").write_text(
        "Absender: Kanzlei Alpha\nAktenvermerk vom 03.04.2020. Strittiger Betrag: 100 EUR.", encoding="utf-8",
    )
    (workspace.inbox_dir / "schreiben_2021.txt").write_text(
        "Schreiben vom 05.06.2021. Strittiger Betrag: 200 EUR.", encoding="utf-8",
    )
    (workspace.inbox_dir / "secret_private.txt").write_text(
        "Beklagter: PRIVATE PERSON NAME\nTOP SECRET PRIVATE NAME; Termin am 09.09.2025; 999 EUR.", encoding="utf-8",
    )
    assert quick_organize_inbox()["imported_files"] == 3
    rows = read_register_rows()
    by_name = {row["original_name"]: row for row in rows}
    a, b, private = (by_name["gericht_2020.txt"],
                     by_name["schreiben_2021.txt"],
                     by_name["secret_private.txt"])
    for row in rows:
        row["selected_for_export"] = ("no" if row["file_id"] == private["file_id"] else "yes")
    write_register_rows(rows)
    for row in (a, b):
        index_document(row["file_id"])
    return workspace, a, b, private


def test_synthesis_is_source_bound_and_does_not_mutate_original_records(tmp_path, monkeypatch):
    workspace, a, b, private = _case(tmp_path, monkeypatch)
    write_entity_rows([
        {"entity_id": "E1", "entity_name": "Gericht", "entity_type": "Institution",
         "linked_file_ids": a["file_id"], "notes": "Manuell notiert"},
        {"entity_id": "E2", "entity_name": "PRIVATE PERSON NAME", "entity_type": "Person",
         "linked_file_ids": private["file_id"], "notes": "TOP SECRET PRIVATE"},
    ])
    write_timeline_rows([
        {"event_id": "EV-A", "event_date": "2020-04-03",
         "event_title": "Operator states that a letter arrived",
         "linked_file_ids": a["file_id"], "status": "draft"},
        {"event_id": "EV-PRIVATE", "event_date": "2025-09-09",
         "event_title": "TOP SECRET PRIVATE EVENT",
         "linked_file_ids": private["file_id"], "status": "draft"},
        {"event_id": "EV-MIXED", "event_date": "2020-04-03",
         "event_title": "TOP SECRET MIXED CONTEXT",
         "linked_file_ids": a["file_id"] + "," + private["file_id"], "status": "draft"},
    ])
    claim_a = add_claim(a["file_id"], 1, "Strittiger Betrag: 100 EUR",
                        "Amount may be reported as 100 EUR")
    claim_b = add_claim(b["file_id"], 1, "Strittiger Betrag: 200 EUR",
                        "Amount may be reported as 200 EUR")
    add_comparison(claim_a["claim_id"], "betrag", "amount", "100")
    add_comparison(claim_b["claim_id"], "betrag", "amount", "200")

    before = (workspace.register_dir / "document_register.csv").read_bytes()
    whole = case_narrative()
    dates = [item["date"] for item in whole["chronology"]]
    assert dates == sorted(dates)
    assert whole["counts"]["potential_value_differences"] == 1
    assert whole["potential_differences"][0]["status"] == "potential_difference_needs_human_review"
    assert all(row["source_kind"] != "confirmed_fact" for row in whole["chronology"])
    assert whole["counts"]["participants"] == 2
    assert any(p["name"] == "Kanzlei Alpha" for p in whole["participant_hints"])
    assert any(p["name"] == "PRIVATE PERSON NAME" for p in whole["participant_hints"])
    assert (workspace.register_dir / "document_register.csv").read_bytes() == before

    selected = case_narrative({a["file_id"], b["file_id"]})
    assert selected["scope"] == "selected_originals_only"
    assert selected["counts"]["documents"] == 2
    assert selected["counts"]["participants"] == 1
    assert selected["counts"]["participant_hints_unverified"] >= 1
    assert all(p["name"] != "PRIVATE PERSON NAME" for p in selected["participant_hints"])
    assert selected["counts"]["potential_value_differences"] == 1
    assert all(private["file_id"] not in row["file_ids"] for row in selected["chronology"])
    assert all("TOP SECRET" not in row["title"] for row in selected["chronology"])
    assert all(private["file_id"] not in row["file_ids"] for row in selected["participants"])

    folder = build_export_package()
    with ZipFile(folder.with_suffix(".zip")) as archive:
        assert "SACHVERHALT_ARBEITSSTAND.md" in archive.namelist()
        guide = archive.read("SACHVERHALT_ARBEITSSTAND.md").decode("utf-8")
        assert "Chronologischer Arbeitsstand" in guide
        assert "Mögliche Wertabweichungen" in guide
        assert "Absender: Kanzlei Alpha" in guide
        assert "Strittiger Betrag: 100 EUR" in guide
        assert "Strittiger Betrag: 200 EUR" in guide
        assert a["file_id"] in guide and b["file_id"] in guide
        assert private["file_id"] not in guide
        assert "TOP SECRET" not in guide
        assert "PRIVATE PERSON NAME" not in guide
        assert "09.09.2025" not in guide
        assert "2025-09-09" not in guide
        readme = archive.read("ANWALT_START_HERE.md").decode("utf-8")
        assert "SACHVERHALT_ARBEITSSTAND.md" in readme


def test_invalidated_original_hides_unsupported_value_difference(tmp_path, monkeypatch):
    workspace, a, b, _ = _case(tmp_path, monkeypatch)
    first = add_claim(a["file_id"], 1, "Strittiger Betrag: 100 EUR", "A: 100")
    second = add_claim(b["file_id"], 1, "Strittiger Betrag: 200 EUR", "B: 200")
    add_comparison(first["claim_id"], "wert", "amount", "100")
    add_comparison(second["claim_id"], "wert", "amount", "200")
    assert len(case_narrative()["potential_differences"]) == 1

    original = workspace.originals_dir / b["relative_path"]
    original.write_text("tampered", encoding="utf-8")
    result = case_narrative()
    assert result["potential_differences"] == []
    assert result["limits"]["event_truth_not_determined"] is True
    assert original.read_text(encoding="utf-8") == "tampered"


def test_draft_events_without_source_are_not_fabricated(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    write_timeline_rows([
        {"event_id": "EV-UNLINKED", "event_date": "2022-01-01",
         "event_title": "No linked source", "linked_file_ids": "", "status": "draft"},
        {"event_id": "EV-BADDATE", "event_date": "2022-99-99",
         "event_title": "Impossible date", "linked_file_ids": "DOC-NOT-HERE", "status": "draft"},
    ])
    result = case_narrative()
    assert result["chronology"] == []
    assert result["counts"]["documents"] == 0
    with pytest.raises(ValueError, match="set"):
        case_narrative(["DOC-X"])


def test_one_page_narrative_uses_existing_api_and_escapes_untrusted_content():
    from local_case_organizer.ui.local_case_organizer_ui_narrative import NARRATIVE_SCRIPT
    from local_case_organizer.ui.case_narrative import _md

    assert '"/api/case-narrative"' in NARRATIVE_SCRIPT
    assert "textContent" in NARRATIVE_SCRIPT
    assert "window.LCORefreshWorkspace" in NARRATIVE_SCRIPT
    assert "document.addEventListener" in NARRATIVE_SCRIPT
    assert "lco-narr-people-hints" in NARRATIVE_SCRIPT
    assert "\\#" in _md("# PRIVATE")
