"""Exercise the actual rendered language toggle with a headless Chromium browser.

This test never calls write APIs or reads case data. The HTML is served from a
temporary file, so no local server or real case workspace is touched.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
import subprocess

import pytest


def test_browser_de_en_de_preserves_visible_text_and_unsaved_input(tmp_path):
    browser = next(
        (candidate for candidate in ("google-chrome", "google-chrome-stable",
                                     "chromium", "chromium-browser")
         if shutil.which(candidate)),
        None,
    )
    if browser is None:
        pytest.skip("Headless Chromium unavailable; browser acceptance still required")

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import run
    import local_case_organizer.ui.app as ui
    html = ui.run_ui.__globals__["HTML"]
    probe = r"""
<script>
window.addEventListener('load', () => {
  setTimeout(() => {
    const first = document.getElementById('lang-toggle');
    const get = () => ({
      lang: localStorage.getItem('local_case_organizer_ui_lang'),
      hero: document.querySelector('.hero .lead')?.textContent || '',
      heading: document.querySelector('.hero h1')?.textContent || '',
      nav: document.getElementById('lco-tab-documents')?.textContent || '',
      button: document.querySelector('button[onclick="uploadFiles()"]')?.textContent || '',
      toggle: document.getElementById('lang-toggle')?.textContent || '',
      custom: document.getElementById('new-case-id')?.value || '',
    });
    const result = document.createElement('pre');
    result.id = 'lco-browser-smoke';
    document.body.appendChild(result);
    if (!first) { result.textContent = 'UI_BROWSER_SMOKE_FAIL_NO_TOGGLE'; return; }
    const input = document.getElementById('new-case-id');
    if (input) input.value = 'unsaved-test-case';

    // Force a known starting state without assuming persisted user choices.
    localStorage.setItem('local_case_organizer_ui_lang', 'de');
    window.LCOApplyHumanCopy?.();
    const before = get();
    first.click();
    const english = get();
    first.click();
    const after = get();
    const ok =
      before.lang === 'de' &&
      before.hero.includes('Sammle Dokumente') &&
      before.heading.includes('Deine Unterlagen') &&
      before.nav === 'Dokumente' &&
      english.lang === 'en' &&
      english.hero.includes('Bring documents together') &&
      english.heading.includes('Your documents') &&
      english.nav === 'Documents' &&
      english.button.toLowerCase().includes('add selected') &&
      after.lang === 'de' &&
      after.hero.includes('Sammle Dokumente') &&
      after.nav === 'Dokumente' &&
      after.custom === 'unsaved-test-case';
    result.textContent = ok ? 'UI_BROWSER_SMOKE_OK' : 'UI_BROWSER_SMOKE_FAIL ' + JSON.stringify({before,english,after});
  }, 400);
});
</script>
"""
    # The UI's normal external APIs are unavailable in this isolated file.
    # They are not needed for testing translation or the header controls.
    path = tmp_path / "ui_language_test.html"
    path.write_text(
        html.replace("</body>", probe + "\n</body>"), encoding="utf-8"
    )
    cmd = [
        shutil.which(browser), "--headless=new", "--disable-gpu",
        "--no-sandbox", "--disable-dev-shm-usage",
        "--disable-background-networking",
        "--virtual-time-budget=2600", "--dump-dom", path.as_uri(),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, check=True,
    )
    found = re.search(r'UI_BROWSER_SMOKE_(?:OK|FAIL)[^<]*', result.stdout)
    assert found, f"Browser did not complete language probe: {result.stderr[-1500:]}"
    assert found.group(0) == "UI_BROWSER_SMOKE_OK", found.group(0)
