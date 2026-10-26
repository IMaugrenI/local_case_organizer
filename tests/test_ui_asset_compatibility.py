"""Integration checks through the documented run.py import path."""
import subprocess
import sys
from pathlib import Path


def test_safe_legacy_ui_asset_in_real_runtime_import():
    # CI installs the package, while the top-level asset is activated by run.py.
    program = r"""
import run
from local_case_organizer.ui.local_case_organizer_ui_override import (
    ORDERED_SCRIPT_SAFE,
    _stable_ordered_script,
)
assert "const titles = document.querySelectorAll('.section-title');" not in ORDERED_SCRIPT_SAFE
assert "const buttons = document.querySelectorAll('button');" not in ORDERED_SCRIPT_SAFE
assert "const hints = document.querySelectorAll('.hint');" not in ORDERED_SCRIPT_SAFE
assert "getElementById('lang-toggle')" in ORDERED_SCRIPT_SAFE
assert "localStorage.getItem('local_case_organizer_ui_lang') || 'de'" in ORDERED_SCRIPT_SAFE
assert "html.push(`<li>${item}</li>`)" not in ORDERED_SCRIPT_SAFE
assert "html.push(`<li>${window.escapeHtml(String(item))}</li>`)" in ORDERED_SCRIPT_SAFE
try:
    _stable_ordered_script('<script>unknown future asset</script>')
except RuntimeError:
    pass
else:
    raise AssertionError("Unknown legacy asset was accepted")
print("UI_ASSET_COMPATIBILITY_OK")
"""
    completed = subprocess.run(
        [sys.executable, "-c", program],
        cwd=Path(__file__).resolve().parents[1],
        text=True, capture_output=True, timeout=20, check=True,
    )
    assert "UI_ASSET_COMPATIBILITY_OK" in completed.stdout
