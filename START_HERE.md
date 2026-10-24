# Start here

This is the shortest path for a first-time user.

> German version: [START_HERE_DE.md](START_HERE_DE.md)

## What this tool does

`local_case_organizer` helps you organize sensitive local files into:

1. imported originals with provenance
2. a document register
3. an editable timeline
4. a neutral export package

It is local-first and does not require a cloud service.

It is **not** a legal advice system and does not decide whether a document is legally correct or important.

## Requirements

- Python 3.11+ (`py` or `python` on Windows)
- a local browser for the UI
- enough local disk space for your copied originals and exports

## First start

### Linux

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
bash scripts/linux/start_here.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
pwsh ./scripts/windows/start_here.ps1
```

### macOS

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
./scripts/macos/start_here.command
```

The launcher prepares the local workspace and starts the browser UI.

The UI runs locally. Keep the terminal/process running while you use the UI; stop it with `Ctrl+C`.

## The normal workflow

### 1. Add files

Put files into:

```text
data/inbox/
```

or choose a source through the supported import command/UI.

### 2. Import

```bash
python run.py import
```

The import creates a unique batch, copies originals into `data/originals/`, calculates SHA-256 hashes, and records provenance.

### 3. Build the register

```bash
python run.py build-register
```

### 4. Build the timeline

```bash
python run.py build-timeline
```

### 5. Export

```bash
python run.py export-package
```

Exports are written under `exports/`.

The handoff export intentionally removes absolute local source paths from its provenance view. Selected originals are hash-checked before export.

## Useful checks

```bash
python run.py status
python run.py check
python run.py doctor
```

## Private data boundary

These local runtime folders are ignored by Git:

- `data/`
- `exports/`
- `logs/`
- `workspace/`
- private profiles and archives

Do not post real case files, generated exports, screenshots with private information, or absolute private paths in public GitHub issues.

Read [SECURITY.md](SECURITY.md) before using real sensitive material.

## More detail

- [Beginner guide](docs/guides/beginner_quickstart.md)
- [Install and first test](docs/guides/install_and_first_test.md)
- [Commands](docs/reference/commands.md)
- [Release checklist](docs/release/release_checklist.md)
