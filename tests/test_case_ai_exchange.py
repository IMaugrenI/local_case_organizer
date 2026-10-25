from __future__ import annotations

import csv
import hashlib
import json
import pytest

from local_case_organizer import paths
from local_case_organizer.ai_exchange import (prepare_ai_packet, import_ai_suggestions,
    import_ai_file, read_ai_suggestions, review_ai_suggestion)
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.claims import read_claims
from local_case_organizer.document_text import index_document
from local_case_organizer.register.store import write_register_rows


def _source(root, file_id="DOC-1", text=b"Evidence received on 2026-10-25"):
    p=paths.create_local_workspace(root)
    source=p.originals_dir/"batch"/"statement.txt"
    source.parent.mkdir(parents=True,exist_ok=True)
    source.write_bytes(text)
    with (p.register_dir/"provenance.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=["file_id","stored_relative_path","original_name","sha256"])
        writer.writeheader()
        writer.writerow({"file_id":file_id,"stored_relative_path":"batch/statement.txt",
                        "original_name":"statement.txt","sha256":hashlib.sha256(text).hexdigest()})
    write_register_rows([{"file_id":file_id,"original_name":"statement.txt"}])
    index_document(file_id)
    return source


def _reply(quote="Evidence received", file_id="DOC-1"):
    return {"suggestions":[{"file_id":file_id,"page":1,"source_quote":quote,
                             "statement":"This passage may mention receipt"}]}


def test_offline_packet_and_human_promotion(tmp_path, monkeypatch):
    monkeypatch.setattr(paths,"get_repo_root",lambda:tmp_path/"repo")
    _source(tmp_path/"repo")
    prepared=prepare_ai_packet(["DOC-1"])
    assert prepared["transmitted"] is False
    packet=json.loads(__import__("pathlib").Path(prepared["path"]).read_text())
    assert packet["excerpts"][0]["file_id"]=="DOC-1"
    assert len(read_claims())==0
    imported=import_ai_suggestions(_reply())
    assert imported["accepted_as_pending"]==1
    assert import_ai_suggestions(_reply())["skipped_duplicates"]==1
    record=read_ai_suggestions()[0]
    assert record["status"]=="pending_review"
    outcome=review_ai_suggestion(record["suggestion_id"],"create_draft_claim")
    assert outcome["status"]=="draft_claim_created"
    assert read_claims()[0]["review_status"]=="draft"
    assert review_ai_suggestion(record["suggestion_id"],"create_draft_claim")["linked_claim_id"]==outcome["linked_claim_id"]


def test_invalid_quote_and_modified_source_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(paths,"get_repo_root",lambda:tmp_path/"repo")
    source=_source(tmp_path/"repo")
    with pytest.raises(ValueError,match="absent"):
        import_ai_suggestions(_reply("completely invented quote"))
    import_ai_suggestions(_reply())
    suggestion=read_ai_suggestions()[0]
    source.write_text("Changed original",encoding="utf-8")
    with pytest.raises(ValueError):
        review_ai_suggestion(suggestion["suggestion_id"],"create_draft_claim")
    assert read_claims()==[]


def test_private_case_isolation_and_import_filename_guard(tmp_path, monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda:root)
    create_case(root,"alpha")
    create_case(root,"beta")
    with using_case("alpha"):
        _source(root)
        import_ai_suggestions(_reply())
        assert len(read_ai_suggestions())==1
        with pytest.raises(ValueError,match="filename"):
            import_ai_file("../escape.json")
    with using_case("beta"):
        assert read_ai_suggestions()==[]


def test_untrusted_response_is_not_a_reviewed_fact(tmp_path,monkeypatch):
    monkeypatch.setattr(paths,"get_repo_root",lambda:tmp_path/"repo")
    _source(tmp_path/"repo")
    import_ai_suggestions(_reply())
    record=read_ai_suggestions()[0]
    rejected=review_ai_suggestion(record["suggestion_id"],"reject")
    assert rejected["status"]=="rejected"
    assert read_claims()==[]
