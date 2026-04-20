# local_case_organizer

Local, cloud-free tool for organizing sensitive case documents into structured dossiers, timelines, and export packages.

This repository is a neutral public core for local case organization work. It is designed for people who need to turn chaotic document collections into a cleaner, reviewable dossier without pushing data into a cloud service.

## Use this repo in the simplest way

If you want the shortest safe path, start here:

### Linux

```bash
bash scripts/linux/start_here.sh
```

### Windows PowerShell

```powershell
pwsh ./scripts/windows/start_here.ps1
```

### macOS

```bash
./scripts/macos/start_here.command
```

Backward-compatible root launchers still remain under `scripts/`, but the organized platform folders are now the preferred public reference path.

That path now runs:

1. setup
2. local browser UI

A beginner guide is available in `docs/guides/beginner_quickstart.md`.

## Positioning

`local_case_organizer` is not a law firm system, not a court tool, and not a legal advice engine.

It is a local dossier-building and organization layer.

The goal is simple:

1. keep originals protected
2. assign stable document IDs
3. build a reviewable register
4. support timeline work
5. prepare clean export packages for third parties such as lawyers or advisory services

## Boundary

This repository does **not** claim:

- guaranteed legal correctness
- guaranteed GDPR compliance in every deployment
- automatic legal evaluation
- cloud processing as a default path

This repository is meant to stay technically honest:

- local-first
- cloud-free by default
- privacy-friendly by design
- evidence and provenance aware
- neutral enough for different case types

## Intended users

- private individuals with chaotic case files
- advisory and support contexts
- lawyers as downstream recipients of cleaner dossier exports

## Current command surface

Primary runtime entrypoint:

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

Thin wrapper availability:

- Linux: `scripts/linux/`
- PowerShell: `scripts/windows/`
- macOS: `scripts/macos/`
- compatibility launchers also remain under `scripts/`

## Organized tree

The repository now has an ordered documentation and launcher mirror for easier navigation:

```text
docs/
  guides/
  reference/
  platform/
  roadmap/
  release/

scripts/
  linux/
  windows/
  macos/
```

The operational truth still stays simple:

- one Python runtime entrypoint
- thin OS launchers
- local data outside repository truth

## Local-only testing flow

1. clone the repository locally
2. run the platform `start_here` launcher
3. the browser UI opens locally
4. drop private files into `data/inbox/` or use the inbox folder button from the UI
5. use the large UI buttons for import, register, timeline, and export

## What import adds

The import step is now the provenance anchor for V1.

Each import creates:

- a timestamped batch under `data/originals/`
- a batch-specific `import_manifest_*.csv`
- an aggregate `provenance.csv`

This lets the later document register keep stable file IDs instead of regenerating them blindly on every run.

## What success looks like

A successful first run means:

- your local workspace exists
- the local browser UI opens
- `data/inbox/` is ready for dropped files
- the UI can see your local status cleanly
- later imports produce stable batch and provenance data

## Status

Early V1 scaffold with a working Python-first command path, a first provenance-aware import layer, a browser UI, and a new ordered docs and launcher mirror for Linux, Windows, and macOS.
