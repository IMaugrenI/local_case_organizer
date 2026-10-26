"""B02: existing UI wiring, without changing handlers or data routes."""
import subprocess
import sys
from pathlib import Path

from local_case_organizer.ui.local_case_organizer_ui_experience import (
    EXPERIENCE_CSS,
    EXPERIENCE_SCRIPT,
)


def test_existing_runtime_exposes_workarea_navigation():
    # pytest's installed-package import path differs from the run.py launcher.
    # Exercise the actual documented launcher path in an isolated subprocess.
    script = """
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
print("UI_EXPERIENCE_OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True, timeout=20, check=True,
    )
    assert "UI_EXPERIENCE_OK" in result.stdout


def test_layer_has_no_new_data_calls():
    assert "fetch('/api/" not in EXPERIENCE_SCRIPT
    assert "document.createElement('nav')" in EXPERIENCE_SCRIPT
    assert "groupNode(source(ref),view)" in EXPERIENCE_SCRIPT
    assert "node.hidden=(selected!==view)" in EXPERIENCE_SCRIPT
    assert "target.appendChild(node)" not in EXPERIENCE_SCRIPT
    assert "position:sticky" in EXPERIENCE_CSS
