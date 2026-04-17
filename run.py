#!/usr/bin/env python3
"""Primary local_case_organizer runtime entrypoint."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from local_case_organizer.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
