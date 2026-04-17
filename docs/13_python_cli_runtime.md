# Python CLI runtime

This repo now has a Python-first runtime entrypoint.

## primary entrypoint

```bash
python run.py setup
python run.py check
python run.py status
python run.py doctor
python run.py build-register
python run.py build-timeline
python run.py export-package
```

## wrapper availability

The runtime truth is `python run.py ...`.

Supported convenience wrappers are limited to these files:

- Linux shell wrappers: `scripts/setup.sh`, `scripts/check.sh`, `scripts/status.sh`, `scripts/doctor.sh`
- Windows PowerShell wrappers: `scripts/setup.ps1`, `scripts/check.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`
- macOS command launchers: `scripts/setup.command`, `scripts/check.command`, `scripts/status.command`, `scripts/doctor.command`

## goal

- one operational runtime entrypoint
- cross-platform command handling in Python
- shell and platform launchers stay thin
- local case data remains outside the public repository truth

## command summary

### setup

- creates ignored local workspace folders
- prepares `data/`, `exports/`, `logs/`, and `workspace/`
- prints the next local testing steps

### check

- prints repo and local workspace status as JSON

### status

- prints a concise local workspace summary
- includes file counts and export-package counts

### doctor

- verifies Python runtime details
- checks repo structure presence
- verifies local writeability for key folders

### build-register

- scans `data/originals/`
- writes `data/register/document_register.csv`

### build-timeline

- writes `data/register/timeline.csv`

### export-package

- creates a timestamped handoff folder in `exports/`
- copies current register artifacts into the export bundle
