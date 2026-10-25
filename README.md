# local_case_organizer

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/local_case_organizer_banner_v3_spaced.png" alt="local_case_organizer banner" width="100%" />
</p>

**Turn scattered local documents into an organized, reviewable case file.**

Local Case Organizer helps you import files, assign stable document references, build a register and timeline, and prepare export packages. The workflow stays local by default and is intended for people dealing with **unstructured or sensitive document collections**.

**Get started:** [First run](START_HERE.md) · [German README](README_DE.md) · [ToF Systems overview](https://github.com/IMaugrenI/tof-showcase)

**Workflow:** **Import → Register → Timeline → Export**. Each stage helps make the resulting dossier easier to inspect, discuss, and hand over. The repository is the independent **Structure** tool; it does not perform knowledge retrieval or AI generation by itself.

**Boundary:** this is an organization tool, not a legal-advice engine, court system, or guarantee of legal or regulatory compliance. Review sensitive material before sharing an exported package.

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


## Expansion branch A1–A10 (development preview)

Draft PR #3 contains opt-in isolated cases, source-hash verification,
evidence links, operator-reviewed timeline candidates, optional local PDF/OCR
indexing, source-bound claims, manual mismatch comparisons, metadata-only
edit journaling, browser case selection, neutral dossiers, manual reminders
and an offline AI handoff interface.

The independent **Structure** product still makes **no model calls**:
AI packets can be prepared by explicit user action, but suggestions from
an external local model must be manually imported and individually reviewed.

Example (private case selection, no alternate launcher):

\`\`\`bash
python run.py create-case demo --title "Demo"
python run.py --case demo ui
python run.py --case demo tasks
python run.py --case demo prepare-ai-review DOC-1
\`\`\`

PDF/OCR requires optional local extraction tools; they are not installed
by this repository. All private case data remain in ignored workspaces.

[Development handoff and limitations](docs/roadmap/expansion_handoff.md).

These changes are on a **development branch**, not on main. CI is not
device, operator or release acceptance.
