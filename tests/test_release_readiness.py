"""A16 synthetic release-readiness checks for the existing start architecture."""
from __future__ import annotations

import json
import os
from pathlib import Path

from local_case_organizer import cli, paths
from local_case_organizer.ui.local_case_organizer_ui_workspace import WORKSPACE_SCRIPT


def test_existing_doctor_reports_real_readiness_status(tmp_path, monkeypatch, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "run.py").write_text("# fixture", encoding="utf-8")
    (repo / "src" / "local_case_organizer").mkdir(parents=True)
    monkeypatch.setattr(paths, "get_repo_root", lambda: repo)

    assert cli.cmd_doctor() == 0
    ready = json.loads(capsys.readouterr().out)
    assert ready["ready"] is True
    assert ready["checks"]["python_supported"] is True
    assert all(ready["checks"].values())

    original = cli._check_writable
    monkeypatch.setattr(
        cli, "_check_writable", lambda path: False if path.name == "logs" else original(path)
    )
    assert cli.cmd_doctor() == 1
    broken = json.loads(capsys.readouterr().out)
    assert broken["ready"] is False
    assert broken["checks"]["logs_dir_writable"] is False


def test_document_register_can_filter_and_page_beyond_first_200():
    assert "DOCS_PER_PAGE=40" in WORKSPACE_SCRIPT
    assert "cachedDocs.slice(0,200)" not in WORKSPACE_SCRIPT
    for needle in (
        "lco-ws-doc-filter", "lco-ws-doc-page-info", "lco-ws-doc-prev",
        "lco-ws-doc-next", "const filtered=cachedDocs.filter",
        "docDrafts.set(row.file_id", "docDrafts.get(row.file_id)",
    ):
        assert needle in WORKSPACE_SCRIPT
    assert "textContent" in WORKSPACE_SCRIPT


def test_existing_launchers_stay_in_same_repository_tree():
    root = Path(__file__).resolve().parents[1]
    windows = sorted((root / "scripts" / "windows").glob("*.ps1"))
    mac = sorted((root / "scripts" / "macos").glob("*.command"))
    linux = sorted((root / "scripts" / "linux").glob("*.sh"))
    assert len(windows) >= 10 and len(mac) >= 10 and len(linux) >= 10
    for path in windows:
        body = path.read_text(encoding="utf-8")
        assert 'run.py' in body
        assert '$PythonArgs = @("-3")' in body
        assert "sys.version_info >= (3, 11)" in body
    for path in [root / "scripts/linux/start_here.sh",
                 root / "scripts/macos/start_here.command"]:
        content = path.read_text(encoding="utf-8")
        assert "set -euo pipefail" in content
        assert "sys.version_info >= (3, 11)" in content
        assert "run.py setup" in content and "run.py ui" in content
    if os.name != "nt":
        for path in mac:
            assert os.access(path, os.X_OK), "macOS .command must be executable"
