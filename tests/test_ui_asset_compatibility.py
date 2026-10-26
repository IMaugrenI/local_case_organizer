"""Integration assertions for layered language, rendering and safe HTML."""
from local_case_organizer.ui.local_case_organizer_ui_override import (
    ORDERED_SCRIPT_SAFE,
    _stable_ordered_script,
)


def test_index_based_legacy_translation_is_disabled():
    assert "const titles = document.querySelectorAll('.section-title');" not in ORDERED_SCRIPT_SAFE
    assert "const buttons = document.querySelectorAll('button');" not in ORDERED_SCRIPT_SAFE
    assert "const hints = document.querySelectorAll('.hint');" not in ORDERED_SCRIPT_SAFE
    assert "getElementById('lang-toggle')" in ORDERED_SCRIPT_SAFE
    assert "localStorage.getItem('local_case_organizer_ui_lang') || 'de'" in ORDERED_SCRIPT_SAFE


def test_recent_file_names_cannot_be_injected_as_html():
    assert "html.push(`<li>${item}</li>`)" not in ORDERED_SCRIPT_SAFE
    assert "html.push(`<li>${window.escapeHtml(String(item))}</li>`)" in ORDERED_SCRIPT_SAFE


def test_unknown_legacy_assets_fail_closed():
    try:
        _stable_ordered_script("<script>unknown future asset</script>")
    except RuntimeError:
        return
    raise AssertionError("Unknown asset was silently accepted")
