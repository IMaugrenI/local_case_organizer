"""A12: bounded operator review queue over existing, source-verified case stores.

All fixtures are synthetic; no outside service, real user data, legal inference
or second UI runtime is involved.
"""
from __future__ import annotations

from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.claims import add_claim, set_review_status
from local_case_organizer.document_text import index_document
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.ui.case_briefing import case_briefing
from local_case_organizer.ui.connection_review import review_connection, reviewed_document_hints
from local_case_organizer.ui.quick_intake import quick_organize_inbox


def _case(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    for name, text in {
        "alpha.txt": "Aktenzeichen: 33 Ca 222/25\nZeuge: Alice\nAussage: 120 EUR\n",
        "beta.txt": "Geschäftszeichen: 33 Ca 222/25\nSachverhalt offen.\n",
        "gamma.txt": "Az.: 33 Ca 222/25\nUngeprüfter Zusatz.\n",
    }.items():
        (workspace.inbox_dir / name).write_text(text, encoding="utf-8")
    assert quick_organize_inbox()["imported_files"] == 3
    rows = read_register_rows()
    for row in rows:
        index_document(row["file_id"])
    return workspace, {row["original_name"]: row for row in rows}


def test_cockpit_uses_verified_existing_review_states(tmp_path, monkeypatch):
    _workspace, docs = _case(tmp_path, monkeypatch)
    claim = add_claim(docs["alpha.txt"]["file_id"], 1, "Aussage: 120 EUR",
                      "Eine Quelle nennt den Betrag 120 EUR.")
    first = case_briefing()
    assert first["totals"]["documents"] == 3
    assert first["totals"]["claim_review_pending"] == 1
    assert first["totals"]["claim_recheck_required"] == 0
    assert first["totals"]["connection_review_pending"] == 1
    assert len(first["review_queue"]["document_samples"]) == 3
    assert first["review_queue"]["claim_samples"][0]["claim_id"] == claim["claim_id"]
    assert first["review_queue"]["claim_samples"][0]["source_quote"] == "Aussage: 120 EUR"
    assert first["review_queue"]["claim_samples"][0]["status"] == "pending_review"
    assert first["review_queue"]["connection_samples"][0]["status"] == "pending_review"
    assert first["review_queue"]["operator_review_is_not_factual_or_legal_confirmation"] is True

    set_review_status(claim["claim_id"], "reviewed")
    group = reviewed_document_hints()["groups"][0]
    review_connection(group["group_id"], group["source_signature"],
                      "accepted_as_organizational_link")
    completed = case_briefing()
    assert completed["totals"]["claim_review_pending"] == 0
    assert completed["totals"]["connection_review_pending"] == 0
    assert completed["review_queue"]["claim_samples"] == []
    assert completed["review_queue"]["connection_samples"] == []


def test_stale_reviewed_claim_does_not_expose_unverified_text(tmp_path, monkeypatch):
    workspace, docs = _case(tmp_path, monkeypatch)
    claim = add_claim(docs["alpha.txt"]["file_id"], 1, "Aussage: 120 EUR",
                      "Never publish this unverified statement")
    set_review_status(claim["claim_id"], "reviewed")
    source = workspace.originals_dir / docs["alpha.txt"]["relative_path"]
    source.write_text("Original wurde geändert", encoding="utf-8")
    report = case_briefing()
    assert report["totals"]["claim_review_pending"] == 0
    assert report["totals"]["claim_recheck_required"] == 1
    stale = report["review_queue"]["claim_samples"][0]
    assert stale["status"] == "recheck_required"
    assert stale["statement"] == "" and stale["source_quote"] == ""
    assert "Never publish this unverified statement" not in str(report["review_queue"])


def test_connection_recheck_and_case_isolation(tmp_path, monkeypatch):
    workspace, _docs = _case(tmp_path, monkeypatch)
    group = reviewed_document_hints()["groups"][0]
    review_connection(group["group_id"], group["source_signature"], "dismissed")
    assert case_briefing()["totals"]["connection_review_pending"] == 0
    create_case(workspace.repo_root, "second")
    with using_case("second"):
        empty = case_briefing()
        assert empty["totals"]["documents"] == 0
        assert empty["totals"]["claim_review_pending"] == 0
        assert empty["review_queue"]["document_samples"] == []
        assert empty["review_queue"]["claim_samples"] == []
        assert empty["review_queue"]["connection_samples"] == []
    assert case_briefing()["totals"]["documents"] == 3


def test_cockpit_is_existing_browser_and_explicit_action_only():
    from local_case_organizer.ui.local_case_organizer_ui_briefing import BRIEFING_SCRIPT
    assert 'id="lco-brief-review"' in BRIEFING_SCRIPT
    assert '"/api/case-briefing"' in BRIEFING_SCRIPT
    assert '"/api/review-claim"' in BRIEFING_SCRIPT
    assert "window.confirm(t(\"reviewConfirmClaim\"))" in BRIEFING_SCRIPT
    assert "textContent" in BRIEFING_SCRIPT
    assert 'openPanel("lco-narrative")' in BRIEFING_SCRIPT
    assert 'openPanel("lco-ws-documents")' in BRIEFING_SCRIPT
