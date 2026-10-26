"""B02: existing UI wiring, no changes to routes or workflow controls."""
from local_case_organizer.ui.local_case_organizer_ui_experience import EXPERIENCE_CSS, EXPERIENCE_SCRIPT


def test_existing_runtime_exposes_workarea_navigation():
    import run
    import local_case_organizer.ui.app as ui
    html = ui.run_ui.__globals__["HTML"]
    assert "lco-workspace-nav" in html
    assert "VIEWS=[" in html
    assert "Dokumente" in html and "Beziehungen" in html
    assert "lco-workspace-view[hidden]" in html
    assert 'id="case-selector"' in html
    assert 'id="fileInput"' in html
    assert 'id="task-board"' in html
    assert 'id="ai-review-result"' in html
    assert 'onclick="uploadFiles()"' in html
    assert 'onclick="saveRegister()"' in html


def test_layer_has_no_new_data_calls():
    assert "fetch('/api/" not in EXPERIENCE_SCRIPT
    assert "document.createElement('section')" in EXPERIENCE_SCRIPT
    assert "target.appendChild(node)" in EXPERIENCE_SCRIPT
    assert "position:sticky" in EXPERIENCE_CSS
