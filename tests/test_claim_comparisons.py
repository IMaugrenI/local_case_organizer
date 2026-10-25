from __future__ import annotations
import csv
import hashlib
import pytest
from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.claims import add_claim
from local_case_organizer.comparison import add_comparison, comparison_report
from local_case_organizer.document_text import index_document
from local_case_organizer.register.store import write_register_rows

def _make_doc(root, file_id, filename, statement):
    p = paths.create_local_workspace(root)
    path = p.originals_dir / "batch" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = statement.encode("utf-8")
    path.write_bytes(payload)
    provenance = p.register_dir / "provenance.csv"
    rows = []
    if provenance.exists():
        with provenance.open("r", encoding="utf-8", newline="") as fd:
            rows = list(csv.DictReader(fd))
    fields = ["file_id", "stored_relative_path", "sha256", "original_name"]
    with provenance.open("w", encoding="utf-8", newline="") as fd:
        writer = csv.DictWriter(fd, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        writer.writerow({"file_id": file_id,"stored_relative_path": "batch/"+filename,
                         "sha256": hashlib.sha256(payload).hexdigest(),"original_name":filename})
    existing = []
    from local_case_organizer.register.store import read_register_rows
    existing = read_register_rows()
    write_register_rows([*existing, {"file_id":file_id,"original_name":filename}])
    index_document(file_id)
    return add_claim(file_id, 1, statement[:16], "Amount mentioned in the source")

def test_explicit_cross_document_mismatch_and_normalization(tmp_path,monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda: root)
    a=_make_doc(root,"DOC-1","a.txt","Invoice total: 120.00")
    b=_make_doc(root,"DOC-2","b.txt","Invoice total: 130.00")
    assert comparison_report()["review_candidates"]==[]
    add_comparison(a["claim_id"],"invoice-total","amount","120,00")
    assert comparison_report()["review_candidates"]==[]
    add_comparison(b["claim_id"],"invoice-total","amount","130.00")
    report=comparison_report()
    assert report["review_candidates"][0]["status"]=="potential_mismatch_needs_human_review"
    assert len(report["review_candidates"][0]["sources"])==2

def test_same_value_or_same_source_does_not_imply_mismatch(tmp_path,monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda: root)
    a=_make_doc(root,"DOC-1","a.txt","Invoice total: 120.00")
    b=_make_doc(root,"DOC-2","b.txt","Invoice total: 120.00")
    add_comparison(a["claim_id"],"invoice","amount","120,00")
    add_comparison(b["claim_id"],"invoice","amount","120.00")
    assert comparison_report()["review_candidates"]==[]

def test_case_isolation_and_source_integrity(tmp_path,monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda: root)
    create_case(root,"first")
    create_case(root,"second")
    with using_case("first"):
        a=_make_doc(root,"DOC-1","first.txt","Invoice total: 120.00")
        add_comparison(a["claim_id"],"invoice","amount","120.00")
    with using_case("second"):
        assert comparison_report()["records"]==[]
        with pytest.raises(ValueError,match="not registered"):
            add_comparison(a["claim_id"],"invoice","amount","120.00")

def test_invalid_value_and_duplicate_topic(tmp_path,monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda: root)
    a=_make_doc(root,"DOC-1","a.txt","Invoice total: 120.00")
    with pytest.raises(ValueError,match="Date"):
        add_comparison(a["claim_id"],"deadline","date","31.02.2026")
    add_comparison(a["claim_id"],"invoice","amount","120.00")
    with pytest.raises(ValueError,match="already"):
        add_comparison(a["claim_id"],"invoice","amount","100.00")
