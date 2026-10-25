from __future__ import annotations

import csv
import hashlib

import pytest

from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.claims import add_claim, read_claims, set_review_status
from local_case_organizer.document_text import get_indexed, index_document, search_text
from local_case_organizer.graph import evidence_graph
from local_case_organizer.register.store import write_register_rows


def _imported(root, file_id, filename, payload):
    p = paths.create_local_workspace(root)
    original = p.originals_dir / "batch" / filename
    original.parent.mkdir(parents=True, exist_ok=True)
    original.write_bytes(payload)
    provenance = p.register_dir / "provenance.csv"
    existing = []
    if provenance.exists():
        with provenance.open("r", encoding="utf-8", newline="") as handle:
            existing = list(csv.DictReader(handle))
    fields = ["file_id", "stored_relative_path", "sha256", "original_name"]
    with provenance.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(existing)
        writer.writerow({"file_id": file_id, "stored_relative_path": "batch/" + filename,
                         "sha256": hashlib.sha256(payload).hexdigest(), "original_name": filename})
    write_register_rows([{"file_id": file_id, "original_name": filename}])
    return original


def test_index_search_claim_review_and_integrity_guard(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    original = _imported(root, "DOC-1", "note.txt", b"On 24 October Alice delivered the receipt.\n")
    result = index_document("DOC-1")
    assert result["status"] == "indexed_locally"
    assert result["method"] == "plaintext"
    hits = search_text("receipt")["matches"]
    assert len(hits) == 1 and hits[0]["file_id"] == "DOC-1"
    claim = add_claim("DOC-1", 1, "Alice delivered the receipt", "Receipt delivery is stated")
    assert claim["review_status"] == "draft"
    assert read_claims()[0]["source_quote"] == "Alice delivered the receipt"
    assert set_review_status(claim["claim_id"], "reviewed")["review_status"] == "reviewed"
    assert {"source": "claim:" + claim["claim_id"], "target": "file:DOC-1",
            "relation": "quoted_source"} in evidence_graph()["edges"]
    original.write_bytes(b"changed")
    assert search_text("receipt")["matches"] == []
    with pytest.raises(ValueError):
        add_claim("DOC-1", 1, "Alice delivered the receipt", "Still valid?")
    with pytest.raises(ValueError):
        set_review_status(claim["claim_id"], "reviewed")


def test_cases_have_independent_text_index_and_claims(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    create_case(root, "alpha")
    create_case(root, "beta")
    with using_case("alpha"):
        _imported(root, "DOC-1", "alpha.txt", b"Only in alpha: 123456.")
        index_document("DOC-1")
        add_claim("DOC-1", 1, "Only in alpha", "A claim for alpha")
    with using_case("beta"):
        assert search_text("alpha")["matches"] == []
        assert read_claims() == []
        with pytest.raises(ValueError):
            get_indexed("DOC-1")


def test_refuses_unsupported_ocr_without_explicit_optin(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    _imported(root, "DOC-1", "image.png", b"not a real image")
    with pytest.raises(ValueError, match="opt-in"):
        index_document("DOC-1")
    with pytest.raises(ValueError, match="verbatim"):
        _imported(root, "DOC-2", "other.txt", b"Another entry.")
        index_document("DOC-2")
        add_claim("DOC-2", 1, "quote not present", "This is a statement")


def test_rejects_forged_id_or_page(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    _imported(root, "DOC-1", "note.txt", b"Evidence quote is here")
    index_document("DOC-1")
    with pytest.raises(ValueError, match="page"):
        add_claim("DOC-1", 3, "Evidence quote", "An interpretation")
    with pytest.raises(ValueError):
        index_document("../escape")


def test_corrupted_index_is_rejected(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    _imported(root, "DOC-1", "note.txt", b"Quote of evidence.")
    index_document("DOC-1")
    from local_case_organizer.document_text import _index_path
    target = _index_path("DOC-1")
    target.write_text('{"version":1,"file_id":"DOC-1","pages":["corrupted"]}', encoding="utf-8")
    with pytest.raises(ValueError, match="invalid page structure"):
        get_indexed("DOC-1")
