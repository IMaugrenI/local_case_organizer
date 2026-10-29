"""Synthetic full-case local AI review tests; no Ollama or network necessary."""
from __future__ import annotations

from pathlib import Path

import pytest

from local_case_organizer import paths
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.local_model_batch import analyze_next_local_source
from local_case_organizer.ui.autopilot import process_autopilot
from local_case_organizer.ui.quick_intake import quick_organize_inbox
from local_case_organizer.register.store import read_register_rows


def _prepare(tmp_path, monkeypatch, total=3):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    workspace = paths.create_local_workspace()
    for i in range(total):
        (workspace.inbox_dir / f"file-{i}.txt").write_text(
            f"Source text {i}: synthetic review clue.", encoding="utf-8",
        )
    assert quick_organize_inbox()["imported_files"] == total
    assert process_autopilot()["indexed"] == total
    return workspace


def test_batch_resumes_and_skips_completed_sources(tmp_path, monkeypatch):
    area = _prepare(tmp_path, monkeypatch)
    calls = []
    def propose(model, file_ids):
        calls.append((model, tuple(file_ids)))
        return {"accepted_as_pending": 1}
    monkeypatch.setattr("local_case_organizer.local_model_batch.propose_with_local_model", propose)

    first = analyze_next_local_source("qwen2.5:3b", run_token="first")
    assert first["total"] == 3
    assert first["done"] == 1
    assert first["remaining"] == 2
    second = analyze_next_local_source("qwen2.5:3b", run_token="first")
    assert second["done"] == 2
    assert second["remaining"] == 1
    third = analyze_next_local_source("qwen2.5:3b", run_token="first")
    assert third["done"] == 3
    assert third["remaining"] == 0
    assert third["processed_in_step"] == 1
    again = analyze_next_local_source("qwen2.5:3b", run_token="second")
    assert again["processed_in_step"] == 0
    assert len(calls) == 3
    assert len({ids for _, ids in calls}) == 3
    journals = list((area.working_dir / "ai_exchange").glob("local_model_*.json"))
    assert len(journals) == 1
    assert journals[0].stat().st_mode & 0o077 == 0
    assert not list(area.exports_dir.iterdir())
    assert len(read_register_rows()) == 3


def test_retries_each_failure_once_per_explicit_run(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch, total=2)
    calls = []
    fail = True
    def propose(model, file_ids):
        calls.append(file_ids[0])
        if fail:
            raise ValueError("synthetic unavailable model")
        return {"accepted_as_pending": 0}
    monkeypatch.setattr("local_case_organizer.local_model_batch.propose_with_local_model", propose)

    x = analyze_next_local_source("local:1b", run_token="run1")
    assert x["failed"] == 1
    assert x["remaining"] == 1
    y = analyze_next_local_source("local:1b", run_token="run1")
    assert y["failed"] == 2
    assert y["remaining"] == 0

    # A single retry action must not endlessly rerun the same failed file.
    retry_first = analyze_next_local_source(
        "local:1b", retry_failed=True, run_token="retry-one",
    )
    retry_second = analyze_next_local_source(
        "local:1b", retry_failed=True, run_token="retry-one",
    )
    assert retry_first["remaining"] == 1
    assert retry_second["remaining"] == 0
    assert analyze_next_local_source(
        "local:1b", retry_failed=True, run_token="retry-one",
    )["processed_in_step"] == 0

    fail = False
    assert analyze_next_local_source("local:1b", retry_failed=True, run_token="retry-two")["done"] == 1
    assert analyze_next_local_source("local:1b", retry_failed=True, run_token="retry-two")["done"] == 2
    assert analyze_next_local_source("local:1b", run_token="third")["remaining"] == 0
    assert len(calls) == 6


@pytest.mark.parametrize("model,retry,token", [
    ("http://example.com", False, "run"),
    ("../private", False, "run"),
    ("local:1b", True, ""),
    ("local:1b", False, "../outside"),
])
def test_batch_rejects_unsafe_selection_and_tokens(tmp_path, monkeypatch, model, retry, token):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path / "repo")
    with pytest.raises(ValueError):
        analyze_next_local_source(model, retry_failed=retry, run_token=token)


def test_case_progress_does_not_cross_case_boundaries(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    create_case(root, "case-a", "Synthetic A")
    create_case(root, "case-b", "Synthetic B")
    monkeypatch.setattr("local_case_organizer.local_model_batch.propose_with_local_model",
                        lambda model, ids: {"accepted_as_pending": 0})
    with using_case("case-a"):
        _prepare(tmp_path, monkeypatch, 1)
        one = analyze_next_local_source("local:1b", run_token="first")
        assert one["total"] == 1 and one["done"] == 1
    with using_case("case-b"):
        two = analyze_next_local_source("local:1b", run_token="second")
        assert two["total"] == 0
        assert two["done"] == 0
