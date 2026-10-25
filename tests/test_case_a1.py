from __future__ import annotations

import csv
import hashlib

import pytest

from local_case_organizer import paths
from local_case_organizer.cases import create_case, get_active_case, list_cases, using_case
from local_case_organizer.graph import evidence_graph
from local_case_organizer.integrity import recent_integrity_runs, verify_integrity
from local_case_organizer.register.store import REGISTER_FIELDS, write_register_rows
from local_case_organizer.timeline.store import TIMELINE_FIELDS, write_timeline_rows


def test_scoped_cases_are_isolated_and_legacy_unchanged(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    legacy = paths.create_local_workspace()
    assert legacy.data_dir == root / "data"
    create_case(root, "alpha", "Alpha")
    create_case(root, "beta", "Beta")
    assert [x["case_id"] for x in list_cases(root)] == ["alpha", "beta"]
    with using_case("alpha"):
        a = paths.create_local_workspace()
        (a.register_dir / "marker.txt").write_text("alpha")
        assert get_active_case() == "alpha"
        assert a.data_dir != legacy.data_dir
    with using_case("beta"):
        b = paths.create_local_workspace()
        assert not (b.register_dir / "marker.txt").exists()
    assert get_active_case() is None


def test_invalid_case_ids_and_missing_case_block(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    for bad in ("../bad", "/etc", "UPPER", "a.b"):
        with pytest.raises(ValueError):
            create_case(root, bad)
    with using_case("missing"):
        with pytest.raises(ValueError, match="Unknown case"):
            paths.create_local_workspace()


def test_integrity_and_link_graph(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    create_case(root, "alpha")
    with using_case("alpha"):
        p = paths.get_workspace_paths()
        original = p.originals_dir / "batch" / "evidence.txt"
        original.parent.mkdir(parents=True)
        original.write_bytes(b"evidence")
        digest = hashlib.sha256(b"evidence").hexdigest()
        with (p.register_dir / "provenance.csv").open("w", encoding="utf-8", newline="") as fd:
            w = csv.DictWriter(fd, fieldnames=["file_id", "stored_relative_path", "sha256"])
            w.writeheader()
            w.writerow({"file_id": "DOC-1", "stored_relative_path": "batch/evidence.txt", "sha256": digest})
        write_register_rows([{"file_id": "DOC-1", "original_name": "evidence.txt"}])
        write_timeline_rows([{"event_id": "EV-1", "event_title": "An event", "linked_file_ids": "DOC-1"}])
        graph = evidence_graph()
        assert graph["edges"] == [{"source": "event:EV-1", "target": "file:DOC-1",
                                   "relation": "linked_file"}]
        result = verify_integrity()
        assert result["results"] == {"ok": 1}
        original.write_bytes(b"changed")
        assert verify_integrity()["results"] == {"hash_mismatch": 1}
        assert len(recent_integrity_runs()) == 2
    with using_case("beta"):
        with pytest.raises(ValueError, match="Unknown case"):
            paths.get_workspace_paths()
