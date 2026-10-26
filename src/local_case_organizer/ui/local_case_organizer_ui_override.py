from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from local_case_organizer_ui_assets import ORDERED_CSS, ORDERED_SCRIPT
from .local_case_organizer_ui_fixups import FIXUP_CSS, FIXUP_SCRIPT
from .local_case_organizer_ui_theme_fixups import THEME_FIXUP_CSS, THEME_FIXUP_SCRIPT
from .local_case_organizer_ui_experience import EXPERIENCE_CSS, EXPERIENCE_SCRIPT

ORIGINAL_UI_PATH = Path(__file__).resolve().parent / 'app.py'
ORIGINAL_MODULE_NAME = '_local_case_organizer_original_ui'

_NEXT_STEP_TEXT_TO_KEY = {
    'Next step: add files through the upload area or open the inbox folder and place files there.': 'next_step_add_files',
    "Next step: use 'Import inbox files' to move your waiting files into a tracked import batch.": 'next_step_import_waiting',
    "Next step: use 'Build register' to create your document register.": 'next_step_build_register',
    "Next step: mark the important register rows with 'selected_for_export = yes' so the handoff package knows what to include.": 'next_step_select_export',
    'Next step: create your first export package.': 'next_step_first_export',
    'Your workspace already has imports, working tables, and exports. Use the browser tables to keep the dossier current.': 'next_step_workspace_ready',
    'Use the main action buttons below.': 'next_step_use_buttons',
    'Nächster Schritt: Dateien über den Upload-Bereich hinzufügen oder den Inbox-Ordner öffnen und dort Dateien hineinlegen.': 'next_step_add_files',
    "Nächster Schritt: 'Inbox-Dateien importieren' nutzen, damit wartende Dateien in einen verfolgten Import-Batch übernommen werden.": 'next_step_import_waiting',
    "Nächster Schritt: 'Register bauen' nutzen, um dein Dokumentenregister zu erstellen.": 'next_step_build_register',
    "Nächster Schritt: wichtige Register-Zeilen mit 'selected_for_export = yes' markieren, damit das Exportpaket weiß, was enthalten sein soll.": 'next_step_select_export',
    'Nächster Schritt: dein erstes Exportpaket erstellen.': 'next_step_first_export',
    'Dein Arbeitsbereich hat bereits Importe, Arbeitstabellen und Exporte. Nutze die Browser-Tabellen, um das Dossier aktuell zu halten.': 'next_step_workspace_ready',
    'Nutze die Hauptaktions-Buttons unten.': 'next_step_use_buttons',
}

_NEXT_STEP_KEY_TO_TEXT = {
    'next_step_add_files': 'Next step: add files through the upload area or open the inbox folder and place files there.',
    'next_step_import_waiting': "Next step: use 'Import inbox files' to move your waiting files into a tracked import batch.",
    'next_step_build_register': "Next step: use 'Build register' to create your document register.",
    'next_step_select_export': "Next step: mark the important register rows with 'selected_for_export = yes' so the export package knows what to include.",
    'next_step_first_export': 'Next step: create your first export package.',
    'next_step_workspace_ready': 'Your workspace already has imports, working tables, and exports. Use the browser tables to keep the dossier current.',
    'next_step_use_buttons': 'Use the main action buttons below.',
}

spec = importlib.util.spec_from_file_location(ORIGINAL_MODULE_NAME, ORIGINAL_UI_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f'Could not load original UI module from {ORIGINAL_UI_PATH}')
_original = importlib.util.module_from_spec(spec)
sys.modules[ORIGINAL_MODULE_NAME] = _original
spec.loader.exec_module(_original)

_original_status_payload = getattr(_original, '_status_payload', None)


def _normalized_status_payload() -> dict[str, object]:
    if not callable(_original_status_payload):
        raise RuntimeError('Original UI module does not expose a callable _status_payload')
    payload = _original_status_payload()
    if not isinstance(payload, dict):
        return payload
    next_step_key = payload.get('next_step_key')
    next_step_text = payload.get('next_step')
    if not next_step_key and hasattr(_original, '_next_step_key') and callable(_original._next_step_key):
        next_step_key = _original._next_step_key()
    if not next_step_key and isinstance(next_step_text, str):
        next_step_key = _NEXT_STEP_TEXT_TO_KEY.get(next_step_text)
    if not next_step_text and isinstance(next_step_key, str):
        next_step_text = _NEXT_STEP_KEY_TO_TEXT.get(next_step_key)
    payload['next_step_key'] = next_step_key or 'next_step_use_buttons'
    payload['next_step'] = next_step_text or _NEXT_STEP_KEY_TO_TEXT['next_step_use_buttons']
    return payload


_original._status_payload = _normalized_status_payload

def _stable_ordered_script(source: str) -> str:
    """Keep legacy translations/renderers but drop unsafe positional DOM edits.

    New case features add sections and actions; their ordering is not a stable
    localization contract. Existing fixup and experience scripts use known IDs
    and onclick handlers instead.
    """
    first = "      const titles = document.querySelectorAll('.section-title');"
    last = "      const langToggle = document.getElementById('lang-toggle');"
    start = source.find(first)
    stop = source.find(last, start)
    if start < 0 or stop <= start:
        raise RuntimeError("Unknown ordered UI asset; cannot safely patch positional labels")
    source = source[:start] + "      // Label translations handled by stable DOM selectors.\n" + source[stop:]

    # Do not rebuild HTML from unescaped file names (local script injection).
    unsafe = "items.forEach((item) => html.push(`<li>${item}</li>`));"
    safe = "items.forEach((item) => html.push(`<li>${window.escapeHtml(String(item))}</li>`));"
    if unsafe not in source:
        raise RuntimeError("Unknown recent file renderer; cannot enforce safe text")
    source = source.replace(unsafe, safe, 1)
    # German first-use default. Explicitly selected English remains unchanged.
    language = "localStorage.getItem('local_case_organizer_ui_lang') || 'en'"
    if language not in source:
        raise RuntimeError("Unknown legacy language preference initialization")
    source = source.replace(language, "localStorage.getItem('local_case_organizer_ui_lang') || 'de'", 1)
    # The old asset intentionally delayed a whole-page rewrite by 50 ms.
    # That ran after the keyed localization, visibly toggling words back.
    late_pass = "      setTimeout(applyStatic, 50);"
    if late_pass not in source:
        raise RuntimeError("Unknown legacy UI initialization sequence")
    source = source.replace(late_pass, "      applyStatic();", 1)
    # A language click should perform one full refresh; the renderer pipeline
    # applies the final translated text once data loading has completed.
    eager_pass = "        applyStatic();\n        if (window.refreshAll) window.refreshAll();"
    if eager_pass not in source:
        raise RuntimeError("Unknown legacy language toggle sequence")
    source = source.replace(eager_pass, "        if (window.refreshAll) window.refreshAll();\n        else applyStatic();", 1)
    return source


ORDERED_SCRIPT_SAFE = _stable_ordered_script(ORDERED_SCRIPT)

patched = _original.HTML.replace(
    '</head>',
    ORDERED_CSS + '\n' + FIXUP_CSS + '\n' + THEME_FIXUP_CSS + '\n' + EXPERIENCE_CSS + '\n</head>',
).replace(
    '</body>',
    ORDERED_SCRIPT_SAFE + '\n' + FIXUP_SCRIPT + '\n' + THEME_FIXUP_SCRIPT + '\n' + EXPERIENCE_SCRIPT + '\n</body>',
)
_original.HTML = patched
run_ui = _original.run_ui
__all__ = ['run_ui']
