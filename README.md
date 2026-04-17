# local_case_organizer

Local, cloud-free tool for organizing sensitive case documents into structured dossiers, timelines, and export packages.

This repository is a neutral public core for local case organization work. It is designed for people who need to turn chaotic document collections into a cleaner, reviewable dossier without pushing data into a cloud service.

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

## Core ideas for V1

- preserve originals without silent modification
- create stable file IDs
- store hashes and import metadata
- separate originals, working copies, register data, and exports
- generate a document register
- generate a timeline table
- generate export-ready case packages

## Public vs. private split

This public repository contains only the neutral technical core.

Real case data, private profiles, real names, account numbers, case numbers, and sensitive exports should stay local and must not be committed.

## Current command surface

Primary runtime entrypoint:

```bash
python run.py setup
python run.py check
python run.py status
python run.py doctor
python run.py build-register
python run.py build-timeline
python run.py export-package
```

Thin wrapper availability:

- Linux: `scripts/setup.sh`, `scripts/check.sh`, `scripts/status.sh`, `scripts/doctor.sh`
- PowerShell: `scripts/setup.ps1`, `scripts/check.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`
- macOS: `scripts/setup.command`, `scripts/check.command`, `scripts/status.command`, `scripts/doctor.command`

What these currently do:

- `setup` prepares ignored local folders such as `data/`, `exports/`, and `logs/`
- `check` prints repo and local workspace status
- `status` prints a concise summary of local files and export packages
- `doctor` runs local runtime and writeability checks
- `build-register` scans `data/originals/` and creates `data/register/document_register.csv`
- `build-timeline` creates `data/register/timeline.csv`
- `export-package` creates a timestamped neutral export bundle under `exports/`

## Local-only testing flow

1. clone the repository locally
2. run `python run.py setup`
3. place private test files in `data/originals/`
4. run `python run.py build-register`
5. run `python run.py build-timeline`
6. run `python run.py export-package`

## Planned structure

```text
src/local_case_organizer/
docs/
examples/demo_case/
profiles/default/
```

## Early roadmap

1. repository skeleton and boundary
2. local import and original preservation
3. file ID + hash manifest
4. register and timeline generation
5. export package builder
6. optional local-only helper features later

## Status

Early V1 scaffold with a working Python-first command path.

The first goal is a clean, truthful repo shape before feature growth.
