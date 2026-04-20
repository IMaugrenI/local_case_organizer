# Python CLI runtime

This repo has a Python-first runtime entrypoint.

## Primary entrypoint

```bash
python run.py setup
python run.py check
python run.py status
python run.py doctor
python run.py import
python run.py build-register
python run.py build-timeline
python run.py export-package
python run.py ui
```

## Wrapper availability

The runtime truth is `python run.py ...`.

Supported convenience wrappers are now sorted by platform:

- Linux shell wrappers: `scripts/linux/*.sh`
- Windows PowerShell wrappers: `scripts/windows/*.ps1`
- macOS command launchers: `scripts/macos/*.command`

## Goal

- one operational runtime entrypoint
- cross-platform start logic in Python
- shell wrappers remain thin

## Command summary

### setup

- prepares local runtime directories

### check

- checks repository and local workspace status

### status

- prints a concise local workspace summary

### doctor

- verifies local environment and writeability

### import

- ingests files from the inbox or a selected source path

### build-register

- creates the document register

### build-timeline

- creates the timeline template

### export-package

- builds a timestamped export bundle

### ui

- starts the local browser UI
