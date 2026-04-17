# Commands

## Primary command path

Run all commands from the repository root.

```bash
python run.py check
python run.py init-workspace
python run.py build-register
python run.py build-timeline
python run.py export-package
```

## Command notes

### `python run.py check`
Prints current repository and local workspace status as JSON.

### `python run.py init-workspace`
Creates ignored local folders:

- `data/originals/`
- `data/working/`
- `data/register/`
- `exports/`
- `logs/`
- `workspace/`

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
