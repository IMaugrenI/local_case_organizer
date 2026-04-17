# Commands

## Primary command path

Run all commands from the repository root.

```bash
python run.py setup
python run.py check
python run.py status
python run.py doctor
python run.py build-register
python run.py build-timeline
python run.py export-package
```

## Thin wrapper path

The runtime truth is `python run.py ...`.

Thin wrappers are available for the primary operator commands:

- Linux: `scripts/setup.sh`, `scripts/check.sh`, `scripts/status.sh`, `scripts/doctor.sh`
- PowerShell: `scripts/setup.ps1`, `scripts/check.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`
- macOS: `scripts/setup.command`, `scripts/check.command`, `scripts/status.command`, `scripts/doctor.command`

## Command notes

### `python run.py setup`
Creates ignored local folders:

- `data/originals/`
- `data/working/`
- `data/register/`
- `exports/`
- `logs/`
- `workspace/`

### `python run.py check`
Prints current repository and local workspace status as JSON.

### `python run.py status`
Prints a concise summary of local originals, register files, and export packages.

### `python run.py doctor`
Runs local environment and writeability checks.

### `python run.py build-register`
Scans `data/originals/` and writes `data/register/document_register.csv`.

Current V1 fields:

- `file_id`
- `sha256`
- `original_name`
- `relative_path`
- `suffix`
- `size_bytes`
- `imported_at_utc`
- `review_status`
- `note`

### `python run.py build-timeline`
Creates a starter `data/register/timeline.csv` template.

### `python run.py export-package`
Builds a timestamped export folder in `exports/` and copies current register files into it.

## Local testing rule

Private case material belongs only in ignored local paths and must not be committed.
