from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from local_case_organizer_ui_assets import ORDERED_CSS, ORDERED_SCRIPT

REPO_ROOT = Path(__file__).resolve().parent
ORIGINAL_UI_PATH = REPO_ROOT / "src" / "local_case_organizer" / "ui" / "app.py"
ORIGINAL_MODULE_NAME = "_local_case_organizer_original_ui"

spec = importlib.util.spec_from_file_location(ORIGINAL_MODULE_NAME, ORIGINAL_UI_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load original UI module from {ORIGINAL_UI_PATH}")
_original = importlib.util.module_from_spec(spec)
sys.modules[ORIGINAL_MODULE_NAME] = _original
spec.loader.exec_module(_original)

patched = _original.HTML.replace('</head>', ORDERED_CSS + '\n</head>').replace('</body>', ORDERED_SCRIPT + '\n</body>')
_original.HTML = patched
run_ui = _original.run_ui
__all__ = ["run_ui"]
