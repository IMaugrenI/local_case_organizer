"""B02: single-pass language updates and translated browser messages."""
from __future__ import annotations
import re

from local_case_organizer.ui import app
from local_case_organizer.ui.local_case_organizer_ui_experience import EXPERIENCE_CSS, EXPERIENCE_SCRIPT
from local_case_organizer.ui.local_case_organizer_ui_fixups import FIXUP_SCRIPT
from local_case_organizer.ui.local_case_organizer_ui_theme_fixups import THEME_FIXUP_SCRIPT


def test_navigation_uses_compact_single_row_tabs():
    assert "font-size:.84rem!important" in EXPERIENCE_CSS
    assert "flex-wrap:nowrap!important" in EXPERIENCE_CSS
    assert "overflow-x:auto" in EXPERIENCE_CSS


def test_no_deferred_language_rewrites_or_click_wide_translators():
    assert "setTimeout(applyHumanCopy" not in FIXUP_SCRIPT
    assert "document.addEventListener('click',()=>setTimeout(copy" not in EXPERIENCE_SCRIPT
    assert "setTimeout(copy" not in EXPERIENCE_SCRIPT
    assert "window.LCOApplyExtraCopy=copy" in EXPERIENCE_SCRIPT
    assert "synchronizeCopy();" in FIXUP_SCRIPT
    assert "window.LCOApplyHumanCopy" in FIXUP_SCRIPT
    assert "originalRefreshAll.apply" in FIXUP_SCRIPT


def test_dialogs_and_dynamic_results_are_language_aware():
    html = app.HTML
    assert "window.confirm(uiText('switchStart') + selected + uiText('switchEnd'))" in html
    assert "window.confirm(uiText('aiConfirm'))" in html
    assert "option.value = s; option.textContent = localizedEnum('status',s)" in html
    assert "localizedEnum('status',status)" in html
    assert "uiText('noClaims')" in html
    assert "uiText('noReminders')" in html
    assert "uiText('taskNote')" in html
    assert "uiText('indexing')" in html
    assert "uiText('quote')" in html
    assert "uiText('alreadyAdded')" in html
    assert "uiText('tableNo')" not in html


def test_native_preferences_keep_language_text_values_intact():
    assert "localStorage.getItem('local_case_organizer_ui_lang') || 'de'" in FIXUP_SCRIPT
    assert "localStorage.getItem('local_case_organizer_ui_lang')||'de'" in EXPERIENCE_SCRIPT
    assert "localStorage.getItem('local_case_organizer_ui_lang') || 'de'" in THEME_FIXUP_SCRIPT
    assert "document.getElementById('claim-quote').value" in app.HTML
