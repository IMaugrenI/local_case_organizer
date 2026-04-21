# local_case_organizer

**Organize sensitive case files locally into clean dossiers**

A local, cloud-free tool for turning chaotic document collections into structured registers, timelines, and export packages.

This repository is a neutral public core for local case organization work. It is designed for people who need to turn chaotic document collections into a cleaner, reviewable dossier without pushing data into a cloud service.

## Role in the public product line

Structure (organization and export)

### Works standalone
Yes.

### Can be combined with
- `tof_local_builder` for structuring generated outputs
- `tof_local_knowledge` for organizing extracted evidence

### Not intended for
- triggering generation processes
- acting as a knowledge retrieval system

## Fastest safe start

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

That path runs:

1. setup
2. local browser UI

## Positioning

`local_case_organizer` is not a law firm system, not a court tool, and not a legal advice engine.

It is a local dossier-building and organization layer.

The goal is simple:

1. keep originals protected
2. assign stable document IDs
3. build a reviewable register
4. support timeline work
5. prepare clean export packages for third parties such as lawyers or advisory services

## Intended users

- private individuals with chaotic case files
- advisory and support contexts
- lawyers as downstream recipients of cleaner dossier exports

## Preferred documentation order

- `docs/guides/beginner_quickstart.md`
- `docs/guides/install_and_first_test.md`
- `docs/reference/commands.md`
- `docs/reference/python_cli_runtime.md`
- `docs/platform/linux.md`
- `docs/platform/windows.md`
- `docs/platform/macos.md`
- `docs/roadmap/productization_roadmap.md`
- `docs/roadmap/roadmap_v1.md`
- `docs/release/release_checklist.md`

A documentation map is available in `docs/README.md`.

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

## Runtime truth

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

## Sorted launcher layout

Thin OS launchers now live under:

- `scripts/linux/`
- `scripts/windows/`
- `scripts/macos/`

Common launchers available across the sorted folders:

- `setup`
- `ui`
- `check`
- `status`
- `doctor`
- `import`
- `build-register`
- `build-timeline`
- `export-package`
- `start_here`

## What the commands do

- `setup` prepares ignored local folders such as `data/`, `exports/`, and `logs/`
- `ui` starts the local browser interface
- `check` prints repo and local workspace status
- `status` prints a concise summary of local files, import batches, and export packages
- `doctor` runs local runtime and writeability checks
- `import` ingests files from `data/inbox/` or a chosen source path and writes import manifests
- `build-register` scans imported originals and creates `data/register/document_register.csv`
- `build-timeline` creates `data/register/timeline.csv`
- `export-package` creates a timestamped neutral export bundle under `exports/`

## Local-only testing flow

1. clone the repository locally
2. run the matching `start_here` launcher for your operating system
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

## Current repository shape

```text
run.py
src/local_case_organizer/
docs/
scripts/
examples/demo_case/
profiles/default/
```

## Status

Early V1 scaffold with a working Python-first command path, a local browser UI, sorted documentation folders, and a sorted cross-platform launcher layout.
