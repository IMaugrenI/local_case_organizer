"""Opt-in loopback model contract with synthetic source bytes and no network."""
from __future__ import annotations

import json
import socket

import pytest

from local_case_organizer import paths
from local_case_organizer.ai_exchange import read_ai_suggestions, review_ai_suggestion
from local_case_organizer.claims import read_claims
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.local_model import (
    _local_json, installed_local_models, propose_with_local_model,
)
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.ui.quick_intake import quick_organize_inbox
from local_case_organizer.ui.autopilot import process_autopilot


def case(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    (workspace.inbox_dir / "memo.txt").write_text(
        "Letter dated 2024-02-17: Payment of 100 EUR received by office.",
        encoding="utf-8",
    )
    assert quick_organize_inbox()["imported_files"] == 1
    assert process_autopilot()["indexed"] == 1
    return workspace, read_register_rows()[0]["file_id"]


def test_local_model_verified_pending_hints_and_dedup(tmp_path, monkeypatch):
    workspace, file_id = case(tmp_path, monkeypatch)
    calls = []
    def fake(method, path, payload=None, *, timeout=12):
        calls.append((method, path, timeout))
        if path == "/api/tags":
            return {"models": [{"name": "qwen2.5:3b"}]}
        assert method == "POST" and path == "/api/generate"
        assert payload["model"] == "qwen2.5:3b"
        assert payload["stream"] is False
        assert payload["format"] == "json"
        assert payload["keep_alive"] == "0"
        assert "Letter dated" in payload["prompt"]
        assert "2024-02-17" in payload["prompt"]
        reply = {"suggestions": [
            {"file_id": file_id, "page": 1,
             "source_quote": "Payment of 100 EUR received by office.",
             "statement": "Check the amount and source circumstances."},
            {"file_id": file_id, "page": 1,
             "source_quote": "Fabricated fact never in source",
             "statement": "This assertion is unsupported."},
        ]}
        return {"response": json.dumps(reply)}
    monkeypatch.setattr("local_case_organizer.local_model._local_json", fake)
    assert installed_local_models()["models"] == ["qwen2.5:3b"]
    first = propose_with_local_model("qwen2.5:3b", [file_id])
    assert first["accepted_as_pending"] == 1
    assert first["rejected_unverifiable"] == 1
    assert len(read_ai_suggestions()) == 1
    assert read_ai_suggestions()[0]["status"] == "pending_review"
    assert read_claims() == []
    second = propose_with_local_model("qwen2.5:3b", [file_id])
    assert second["accepted_as_pending"] == 0
    assert second["skipped_duplicates"] == 1
    assert len(read_ai_suggestions()) == 1
    assert len(calls) == 5
    assert list(workspace.exports_dir.iterdir()) == []


def test_model_never_called_for_unverified_changed_original(tmp_path, monkeypatch):
    workspace, file_id = case(tmp_path, monkeypatch)
    original = workspace.originals_dir / read_register_rows()[0]["relative_path"]
    original.write_text("tampered original", encoding="utf-8")
    def unexpected(*args, **kwargs):
        pytest.fail("Model called before verifying original")
    monkeypatch.setattr("local_case_organizer.local_model._local_json", unexpected)
    with pytest.raises(ValueError, match="integrity"):
        propose_with_local_model("qwen2.5:3b", [file_id])
    assert read_ai_suggestions() == []


@pytest.mark.parametrize("model,ids", [
    ("http://example.com:443", ["DOC-1"]),
    ("../../evil", ["DOC-1"]),
    ("qwen2.5:3b", []),
    ("qwen2.5:3b", ["DOC-1"] * 2),
    ("qwen2.5:3b", ["DOC-1", "DOC-2", "DOC-3", "DOC-4"]),
    ("qwen2.5:3b", ["../private"]),
])
def test_invalid_model_or_scope_is_rejected_before_network(monkeypatch, model, ids):
    monkeypatch.setattr("local_case_organizer.local_model._local_json",
                        lambda *args, **kwargs: pytest.fail("No network expected"))
    with pytest.raises(ValueError):
        propose_with_local_model(model, ids)


def test_no_suggestions_when_model_quotes_not_in_verified_source(tmp_path, monkeypatch):
    _, file_id = case(tmp_path, monkeypatch)
    def fake(method, path, payload=None, *, timeout=12):
        if path == "/api/tags":
            return {"models": [{"name": "qwen2.5:3b"}]}
        return {"response": json.dumps({"suggestions": [{
            "file_id": file_id, "page": 1,
            "source_quote": "Entirely fictional quotation",
            "statement": "This could be wrong",
        }]})}
    monkeypatch.setattr("local_case_organizer.local_model._local_json", fake)
    result = propose_with_local_model("qwen2.5:3b", [file_id])
    assert result["accepted_as_pending"] == 0
    assert result["rejected_unverifiable"] == 1
    assert read_ai_suggestions() == []


def test_case_isolation_for_local_model_suggestions(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    create_case(root, "case-a", "A")
    create_case(root, "case-b", "B")
    def fake(method, path, payload=None, *, timeout=12):
        if path == "/api/tags":
            return {"models": [{"name": "local:1b"}]}
        passages = json.loads(payload["prompt"].split("Untrusted source excerpts follow as JSON:\\n", 1)[1])
        return {"response": json.dumps({"suggestions":[{
            "file_id": passages[0]["file_id"], "page": 1,
            "source_quote": "Source passage",
            "statement": "Potential review needed",
        }]})}
    monkeypatch.setattr("local_case_organizer.local_model._local_json", fake)
    with using_case("case-a"):
        w = paths.create_local_workspace()
        (w.inbox_dir / "file.txt").write_text("Source passage from A", encoding="utf-8")
        quick_organize_inbox()
        process_autopilot()
        fid = read_register_rows()[0]["file_id"]
        assert propose_with_local_model("local:1b", [fid])["accepted_as_pending"] == 1
    with using_case("case-b"):
        assert read_ai_suggestions() == []
        assert read_claims() == []


def test_case_briefing_exposes_only_current_source_verified_pending_hints(tmp_path, monkeypatch):
    from local_case_organizer.ui.case_briefing import case_briefing

    area, file_id = case(tmp_path, monkeypatch)
    def fake(method, path, payload=None, *, timeout=12):
        if path == "/api/tags":
            return {"models": [{"name": "qwen2.5:3b"}]}
        return {"response": json.dumps({"suggestions":[{
            "file_id": file_id, "page": 1,
            "source_quote": "Payment of 100 EUR received by office.",
            "statement": "Human review of payment statement recommended.",
        }]})}
    monkeypatch.setattr("local_case_organizer.local_model._local_json", fake)
    assert propose_with_local_model("qwen2.5:3b", [file_id])["accepted_as_pending"] == 1
    before = case_briefing()
    assert before["totals"]["unreviewed_ai_hints"] == 1
    assert before["ai_review_samples"][0]["file_id"] == file_id
    assert before["ai_review_samples"][0]["status"] == "pending_review"
    # Mutating an original invalidates the suggestion in the overview too.
    original = area.originals_dir / read_register_rows()[0]["relative_path"]
    original.write_text("Original was modified.", encoding="utf-8")
    after = case_briefing()
    assert after["totals"]["unreviewed_ai_hints"] == 0
    assert after["ai_review_samples"] == []


def test_local_model_ui_is_explicit_opt_in_on_existing_page():
    from local_case_organizer.ui.local_case_organizer_ui_model import MODEL_SCRIPT
    assert '"/api/local-model-review"' in MODEL_SCRIPT
    assert '"/api/local-models"' in MODEL_SCRIPT
    assert 'window.confirm(t("confirm"))' in MODEL_SCRIPT
    assert 'id="lco-model-box"' not in MODEL_SCRIPT or "lco-model-box" in MODEL_SCRIPT
    assert "document.addEventListener(\"DOMContentLoaded\",init)" in MODEL_SCRIPT
    assert 'lco-special-ai-file' in MODEL_SCRIPT
    assert 'lco-special-ai-reload' in MODEL_SCRIPT


def test_local_client_targets_only_fixed_loopback_and_catches_failures(monkeypatch):
    calls = []
    class FakeHTTP:
        def __init__(self, host, port, timeout):
            calls.append((host, port, timeout))
        def request(self, method, path, **kwargs):
            assert path == "/api/tags" and method == "GET"
        def getresponse(self):
            class Response:
                status = 200
                def read(self, size):
                    return b'{"models":[{"name":"local:1b"}]}'
            return Response()
        def close(self):
            pass
    monkeypatch.setattr("local_case_organizer.local_model.http.client.HTTPConnection", FakeHTTP)
    assert installed_local_models()["models"] == ["local:1b"]
    assert calls == [("127.0.0.1", 11434, 5)]
    with pytest.raises(ValueError, match="Unsupported"):
        _local_json("POST", "http://example.com/private")
