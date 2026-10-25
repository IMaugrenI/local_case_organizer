from __future__ import annotations
import pytest
from local_case_organizer import paths
from local_case_organizer.audit import recent_changes
from local_case_organizer.cases import create_case, using_case
from local_case_organizer.register.store import write_register_rows
from local_case_organizer.entities.store import write_entity_rows
from local_case_organizer.timeline.store import write_timeline_rows

def test_audit_commits_changes_without_plaintext(tmp_path,monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda: root)
    paths.create_local_workspace()
    private="TOP SECRET PERSONAL TEXT"
    write_register_rows([{"file_id":"DOC-1","note":private}])
    write_register_rows([{"file_id":"DOC-1","note":private}]) # no-op
    write_register_rows([{"file_id":"DOC-1","note":"reviewed"}])
    write_timeline_rows([{"event_id":"EV-1","summary":"Case event"}])
    write_entity_rows([{"entity_id":"ENT-1","notes":"Confidential"}])
    changes=recent_changes()
    assert [x["area"] for x in changes] == ["entities","timeline","register","register"]
    journal=paths.get_workspace_paths().register_dir / "change_audit.jsonl"
    raw=journal.read_text(encoding="utf-8")
    assert private not in raw and "Confidential" not in raw
    assert raw.count('"stage": "prepared"') == 4
    assert raw.count('"stage": "committed"') == 4

def test_audit_isolation_per_case(tmp_path,monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda: root)
    create_case(root,"alpha")
    create_case(root,"beta")
    with using_case("alpha"):
        write_register_rows([{"file_id":"DOC-1"}])
        assert len(recent_changes())==1
    with using_case("beta"):
        assert recent_changes()==[]

def test_symlink_journal_blocked_before_data_change(tmp_path,monkeypatch):
    root=tmp_path/"repo"
    monkeypatch.setattr(paths,"get_repo_root",lambda: root)
    p=paths.create_local_workspace()
    other=tmp_path/"external"
    other.write_text("untouched")
    journal=p.register_dir/"change_audit.jsonl"
    try: journal.symlink_to(other)
    except OSError: pytest.skip("No symlink support")
    with pytest.raises(ValueError,match="symlink"):
        write_register_rows([{"file_id":"DOC-1"}])
    assert not (p.register_dir/"document_register.csv").exists()
    assert other.read_text()=="untouched"
