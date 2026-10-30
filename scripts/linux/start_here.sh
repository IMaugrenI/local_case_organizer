#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.11+ is required. Install Python 3 and retry." >&2
  exit 1
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "The available python3 is older than Python 3.11." >&2
  exit 1
fi
python3 run.py setup
python3 run.py ui
