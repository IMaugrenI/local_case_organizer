# Python CLI runtime

This repo now has a Python-first runtime entrypoint.

## Primary entrypoint

```bash
python run.py setup
python run.py ui
python run.py check
python run.py status
python run.py doctor
python run.py import
python run.py import --source /path/to/files
python run.py build-register
python run.py build-timeline
python run.py export-package
```

## Wrapper availability

The runtime truth is `python run.py ...`.

Supported convenience wrappers are grouped by platform:

- Linux shell wrappers: `scripts/linux/`
- Windows PowerShell wrappers: `scripts/windows/`
- macOS command launchers: `scripts/macos/`

Backward-compatible root launchers still exist under `scripts/`.

## Goal

- one operational runtime entrypoint
- cross-platform command handling in Python
- shell and platform launchers stay thin
- local case data remains outside the public repository truth
- import provenance is written before register and export work
- a local browser UI gives normal users a simpler front door

## Command summary

### setup

- creates ignored local workspace folders
- prepares `data/`, `exports/`, `logs/`, and `workspace/`
- prepares `data/inbox/` as a simple user drop zone
- prints the next local testing steps

### ui

- starts the local browser UI
- opens the browser by default
- shows large buttons for the main safe actions
- keeps advanced details in the background

### check

- prints repo and local workspace status as JSON

### status

- prints a concise local workspace summary
- includes inbox file counts, imported file counts, batch counts, and export-package counts

### doctor

- verifies Python runtime details
- checks repo structure presence
- verifies local writeability for key folders

### import

- imports from `data/inbox/` by default
- can import directly from a chosen source path with `--source`
- writes a batch-specific import manifest
- rebuilds aggregate provenance output

### build-register

- scans `data/originals/`
- reads provenance-backed stable file IDs where available
- writes `data/register/document_register.csv`

### build-timeline

- writes `data/register/timeline.csv`

### export-package

- creates a timestamped handoff folder in `exports/`
- copies current register artifacts into the export bundle
- includes provenance output when available
