#!/usr/bin/env python3
"""Primary local_case_organizer runtime entrypoint."""

from pathlib import Path
import importlib.util
import sys

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

OVERRIDE_MODULE_NAME = "local_case_organizer.ui.app"
OVERRIDE_PATH = SRC_DIR / "local_case_organizer" / "ui" / "local_case_organizer_ui_override.py"
if OVERRIDE_PATH.exists():
    spec = importlib.util.spec_from_file_location(OVERRIDE_MODULE_NAME, OVERRIDE_PATH)
    if spec is not None and spec.loader is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[OVERRIDE_MODULE_NAME] = module
        spec.loader.exec_module(module)

from local_case_organizer.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
