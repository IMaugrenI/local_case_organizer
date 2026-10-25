from __future__ import annotations

import pytest

from local_case_organizer import paths
from local_case_organizer.cases import create_case, get_active_case, using_case
from local_case_organizer.ui.case_selection import requested_case


def test_explicit_selection_and_default_legacy(tmp_path):
    root = tmp_path / "repo"
    create_case(root, "alpha", "Alpha")
    create_case(root, "beta", "Beta")
    assert requested_case(None, None, root) is None
    assert requested_case("legacy-default", "alpha", root) is None
    assert requested_case("beta", "alpha", root) == "beta"
    with using_case("alpha"):
        assert requested_case("beta", "alpha", root) == "beta"
        assert get_active_case() == "alpha"


def test_selection_rejects_unsafe_or_unknown_case(tmp_path):
    root = tmp_path / "repo"
    create_case(root, "alpha")
    for label in ("../escape", "/etc", "UNKNOWN", "missing"):
        with pytest.raises(ValueError):
            requested_case(label, None, root)


def test_browser_contains_case_controls():
    from local_case_organizer.ui.app import HTML
    assert 'id="case-selector"' in HTML
    assert "/api/create-case" in HTML
    assert "X-LCO-Case" in HTML


def test_scoped_workspaces_keep_distinct_register_paths(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_repo_root", lambda: root)
    create_case(root, "alpha")
    create_case(root, "beta")
    for case_id in ("alpha", "beta"):
        with using_case(requested_case(case_id, None, root)):
            workspace = paths.create_local_workspace()
            marker = workspace.register_dir / "case_marker.txt"
            marker.write_text(case_id, encoding="utf-8")
    with using_case("alpha"):
        assert (paths.get_workspace_paths().register_dir / "case_marker.txt").read_text() == "alpha"
    with using_case("beta"):
        assert (paths.get_workspace_paths().register_dir / "case_marker.txt").read_text() == "beta"
