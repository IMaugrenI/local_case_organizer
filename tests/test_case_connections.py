"""One-case document connections and selected-only lawyer story regression.

All documents are synthetic, isolated and hash verified. No model, OCR, cloud
or live target instance is required.
"""
from __future__ import annotations

from zipfile import ZipFile

import pytest

from local_case_organizer import paths
from local_case_organizer.document_text import index_document
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.register.store import read_register_rows, write_register_rows
from local_case_organizer.ui.case_connections import linked_document_hints
from local_case_organizer.ui.case_narrative import case_narrative
from local_case_organizer.ui.quick_intake import quick_organize_inbox


def _sources(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    data = {
        "klage.txt": "Aktenzeichen: 2 Ca 1030/21\nSchreiben vom 04.05.2020.\n",
        "urteil.txt": "Geschäftszeichen: 2 Ca 1030/21\nDokument vom 13.11.2021.\n",
        "private.txt": "Az.: 2 Ca 1030/21\nPRIVAT-NUR-DIESE-AKTE\n",
        "unrelated.txt": "Aktenzeichen: 9 F 444/22\nAnderes Verfahren.\n",
        "weak.txt": "Aktenzeichen: abc\nNoch ungeklärt.\n",
    }
    for name, contents in data.items():
        (workspace.inbox_dir / name).write_text(contents, encoding="utf-8")
    assert quick_organize_inbox()["imported_files"] == 5
    rows = read_register_rows()
    by_name = {row["original_name"]: row for row in rows}
    for row in rows:
        row["selected_for_export"] = "yes" if row["original_name"] in ("klage.txt", "urteil.txt") else "no"
        index_document(row["file_id"])
    write_register_rows(rows)
    return workspace, by_name


def test_verified_exact_case_reference_groups_without_promoting_facts(tmp_path, monkeypatch):
    workspace, docs = _sources(tmp_path, monkeypatch)
    report = linked_document_hints()
    assert report["scanned"] == 5
    assert report["verified_text_available"] == 5
    assert len(report["groups"]) == 1
    group = report["groups"][0]
    assert group["reference"] == "2 ca 1030/21"
    assert group["document_count"] == 3
    assert group["status"] == "possible_connection_requires_human_review"
    assert {x["file_id"] for x in group["documents"]} == {
        docs[name]["file_id"] for name in ("klage.txt", "urteil.txt", "private.txt")
    }
    assert all(x["page"] == 1 and "1030/21" in x["source_quote"] for x in group["documents"])
    narrative = case_narrative()
    assert narrative["counts"]["connected_document_groups"] == 1
    assert narrative["case_story_sections"][0]["source_kind"] == (
        "source_verified_same_explicit_reference_unverified_connection"
    )
    assert narrative["limits"]["identical_aktenzeichen_is_only_a_sorting_hint"]
    assert (workspace.inbox_dir / "klage.txt").exists()


def test_export_story_has_no_unselected_document_names_quotes_or_events(tmp_path, monkeypatch):
    workspace, docs = _sources(tmp_path, monkeypatch)
    selected = {docs["klage.txt"]["file_id"], docs["urteil.txt"]["file_id"]}
    full = case_narrative()
    assert full["document_connections"][0]["document_count"] == 3
    restricted = case_narrative(selected)
    assert restricted["document_connections"][0]["document_count"] == 2
    assert len(restricted["case_story_sections"]) == 1
    assert "private.txt" not in str(restricted)
    assert "PRIVAT-NUR-DIESE-AKTE" not in str(restricted)
    assert docs["private.txt"]["file_id"] not in str(restricted)
    folder = build_export_package()
    with ZipFile(folder.with_suffix(".zip")) as bundle:
        assert "SACHVERHALT_ARBEITSSTAND.md" in bundle.namelist()
        narrative = bundle.read("SACHVERHALT_ARBEITSSTAND.md").decode()
        assert "Verknüpfte Unterlagen" in narrative
        assert "2 ca 1030/21" in narrative
        assert "klage.txt" not in narrative or docs["klage.txt"]["file_id"] in narrative
        assert docs["klage.txt"]["file_id"] in narrative
        assert docs["urteil.txt"]["file_id"] in narrative
        assert "private.txt" not in narrative
        assert docs["private.txt"]["file_id"] not in narrative
        assert "PRIVAT-NUR-DIESE-AKTE" not in narrative
        assert "unrelated.txt" not in narrative
        assert "Aktenzeichen: abc" not in narrative


def test_invalidated_or_unindexed_originals_do_not_create_connections(tmp_path, monkeypatch):
    workspace, docs = _sources(tmp_path, monkeypatch)
    first = docs["klage.txt"]
    original = workspace.originals_dir / first["relative_path"]
    original.write_text("Aktenzeichen: 2 Ca 1030/21\nVERÄNDERT\n", encoding="utf-8")
    result = linked_document_hints()
    assert len(result["groups"]) == 1
    assert result["groups"][0]["document_count"] == 2
    assert all(item["file_id"] != first["file_id"]
               for item in result["groups"][0]["documents"])
    assert result["unavailable_or_unindexed"] == 1
    assert result["incomplete"] is True
    assert original.read_text(encoding="utf-8").endswith("VERÄNDERT\n")


def test_exact_reference_required_no_inference_from_shared_date(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    for index in range(2):
        (workspace.inbox_dir / f"doc-{index}.txt").write_text(
            f"Schreiben {index} vom 01.02.2022.\nAktenzeichen: Alpha\n", encoding="utf-8"
        )
    quick_organize_inbox()
    for row in read_register_rows():
        index_document(row["file_id"])
    assert linked_document_hints()["groups"] == []


def test_identical_numbers_of_different_types_do_not_form_false_groups(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    sources = {
        "contract_a.txt": "Vertragsnummer: 5555-88\\nErster Vertragseintrag.\\n",
        "contract_b.txt": "Vertragsnummer: 5555-88\\nZweiter Vertragseintrag.\\n",
        "court.txt": "Aktenzeichen: 5555-88\\nEin Gerichtsdokument.\\n",
        "invoice.txt": "Rechnungsnummer: 5555-88\\nEine Rechnung.\\n",
    }
    for name, text in sources.items():
        (workspace.inbox_dir / name).write_text(text.replace("\\\\n", "\\n"), encoding="utf-8")
    assert quick_organize_inbox()["imported_files"] == 4
    for row in read_register_rows():
        index_document(row["file_id"])
    groups = linked_document_hints()["groups"]
    assert len(groups) == 1
    assert groups[0]["reference_kind"] == "contract"
    assert groups[0]["reference_label"] == "Vertragsnummer"
    assert groups[0]["document_count"] == 2
    assert {source["original_name"] for source in groups[0]["documents"]} == {
        "contract_a.txt", "contract_b.txt"
    }


def test_bad_source_scope_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    with pytest.raises(ValueError, match="set"):
        linked_document_hints(["DOC-ONE"])


def test_one_page_story_shows_links_as_source_data():
    from local_case_organizer.ui.local_case_organizer_ui_narrative import NARRATIVE_SCRIPT
    assert "lco-narr-related" in NARRATIVE_SCRIPT
    assert "case_story_sections" in NARRATIVE_SCRIPT
    assert "textContent" in NARRATIVE_SCRIPT
    assert "document_connections" in NARRATIVE_SCRIPT
