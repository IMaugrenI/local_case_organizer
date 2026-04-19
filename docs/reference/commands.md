# Commands

## Fastest beginner path

If you want the shortest safe path:

```bash
bash scripts/linux/start_here.sh
```

Equivalent entry points:

- PowerShell: `pwsh ./scripts/windows/start_here.ps1`
- macOS: `./scripts/macos/start_here.command`
- backward-compatible root launchers still exist under `scripts/`

That path runs setup and opens the local browser UI.

## Primary command path

Run all commands from the repository root.

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

## Thin wrapper path

The runtime truth is `python run.py ...`.

Thin wrappers are available in platform folders:

- Linux: `scripts/linux/`
- PowerShell: `scripts/windows/`
- macOS: `scripts/macos/`

## Command notes

### `python run.py setup`
Creates ignored local folders:

- `data/inbox/`
- `data/originals/`
- `data/working/`
- `data/register/`
- `exports/`
- `logs/`
- `workspace/`

### `python run.py ui`
Starts the local browser UI on your machine.

The UI offers large buttons and browser editors for:

- prepare workspace
- upload files to the inbox
- import inbox files
- build register
- edit register rows
- build timeline
- edit timeline rows
- edit entities / people / institutions
- build export package
- open inbox folder
- open register folder
- open exports folder
- run doctor

### `python run.py check`
Prints current repository and local workspace status as JSON.

### `python run.py status`
Prints a concise summary of inbox files, imported originals, import batches, register files, selected export rows, entity rows, and export packages.

### `python run.py doctor`
Runs local environment and writeability checks.

### `python run.py import`
Imports files from `data/inbox/` into a timestamped batch under `data/originals/`.

### `python run.py import --source /path/to/files`
Imports directly from a selected file or folder path.

Each import writes:

- a batch-specific `import_manifest_*.csv`
- an aggregate `provenance.csv`

### `python run.py build-register`
Scans `data/originals/` and writes `data/register/document_register.csv`.

### `python run.py build-timeline`
Creates a starter `data/register/timeline.csv` template.

### `python run.py export-package`
Builds a timestamped export folder in `exports/` and prepares a ZIP handoff output.

## Safety markers

- SAFE: `start_here`, `setup`, `ui`, `check`, `status`, `doctor`, `import`, `build-register`, `build-timeline`, `export-package`
- ADVANCED: `import --source /path/to/files`
- DESTRUCTIVE: none in the current public V1 path

## Local testing rule

Private case material belongs only in ignored local paths and must not be committed.
