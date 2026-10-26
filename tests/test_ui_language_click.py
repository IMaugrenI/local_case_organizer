"""Regression for the actual localized-language click in the legacy runtime."""
import subprocess
import sys
from pathlib import Path


def test_legacy_language_click_is_single_pass_and_nondestructive():
    prog = r"""
import run
from local_case_organizer.ui.local_case_organizer_ui_override import ORDERED_SCRIPT_SAFE
start = ORDERED_SCRIPT_SAFE.index('function applyStatic()')
end = ORDERED_SCRIPT_SAFE.index('function patchFunctions()', start)
function = ORDERED_SCRIPT_SAFE[start:end]
assert "hero.querySelector('h1')" not in function
assert "hero.querySelector('.lead')" not in function
assert "document.querySelectorAll('.section-title')" not in function
assert "document.querySelectorAll('button')" not in function
assert "document.querySelectorAll('.hint')" not in function
assert "if (window.LCOApplyHumanCopy) window.LCOApplyHumanCopy();" in ORDERED_SCRIPT_SAFE
assert "if (window.refreshAll) window.refreshAll();" not in ORDERED_SCRIPT_SAFE
assert "localStorage.setItem('local_case_organizer_ui_lang', lang)" in ORDERED_SCRIPT_SAFE
assert "applyStatic();" in ORDERED_SCRIPT_SAFE
print("LANGUAGE_CLICK_SAFE")
"""
    result = subprocess.run(
        [sys.executable, "-c", prog],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True, check=True, timeout=20,
    )
    assert "LANGUAGE_CLICK_SAFE" in result.stdout
