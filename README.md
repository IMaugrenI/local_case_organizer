# local_case_organizer

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/local_case_organizer_banner_v3_spaced.png" alt="local_case_organizer banner" width="100%" />
</p>

**Turn scattered local documents into an organized, reviewable case file.**

Local Case Organizer helps you import files, assign stable document references, build a register and timeline, and prepare export packages. The workflow stays local by default and is intended for people dealing with **unstructured or sensitive document collections**.

**Get started:** [First run](START_HERE.md) · [German README](README_DE.md) · [ToF Systems overview](https://github.com/IMaugrenI/tof-showcase)

**Workflow:** **Import → Register → Timeline → Export**. Each stage helps make the resulting dossier easier to inspect, discuss, and hand over. The repository remains an independent **Structure** tool. An optional connection to an already-running local Ollama model can prepare unreviewed, source-linked hints; no model is called by default.

**Boundary:** this is an organization tool, not a legal-advice engine, court system, or guarantee of legal or regulatory compliance. Review sensitive material before sharing an exported package.

## Role in the public product line

Structure (organization and export)

### Works standalone
Yes.

### Can be combined with
- `tof_local_builder` for structuring generated outputs
- `tof_local_knowledge` for organizing extracted evidence

### Not intended for
- unattended AI fact assertions, legal conclusions or automatic data sharing
- serving as a standalone cloud or knowledge-retrieval platform

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
4. in the **Simple view**, select or create a case
5. select or drop up to 160 files (150 MiB total); the organizer divides the selection into bounded uploads, imports it, then prepares local text/PDF search with visible, resumable progress
6. on the **same simple page**, mark and annotate documents, use local search, timelines, tasks, people and source hints, and explicitly confirm any handoff export. Specialized controls for sourced claims, comparison hints, manual AI handoff and opt-in offline OCR are collapsed under **Other specialized tools**.

The **Organize inbox files** button processes existing inbox documents. Identical content is skipped and original copies remain untouched.

**Case autopilot:** Processing starts only after an intentional file drop/selection and runs in bounded, resumable batches. The case-private progress journal lives in the selected case's `data/working/autopilot_state.json`. Use **Continue processing** after interruption. Registered text files and PDFs are prepared locally for searching when suitable offline tools exist. Unsupported or unreadable files appear as review warnings. The **Explicitly allow local OCR** checkbox is off by default: OCR runs only when selected and installed locally. Automatic case preparation never calls an LLM/cloud, makes legal conclusions, approves uncertain facts or transmits files. A **separately approved, opt-in connection to local Ollama** is described below.

The briefing offers **unverified document-type hints** grounded in filenames or locally verified indexed text. Source-bound date hints from eligible text/PDF sources stay unverified and are included in the lawyer reading guide only for intentionally selected documents. **Select all documents** requires an explicit privacy confirmation; creating an export still requires a separate confirmation.

## Optional on-device AI suggestions (Ollama)

On the existing simple page, expand **Other specialized tools → Optional AI exchange** to discover installed models on a running Ollama service at `127.0.0.1:11434`. The organizer never installs or starts Ollama/models and cannot select other network endpoints.

Only after an explicit click and confirmation are up to **two shortened, hash-verified source excerpts** from the selected document submitted to that loopback service. The model's response must contain an exact quote, document ID and page. Unverifiable suggestions are discarded; valid suggestions remain **pending human review** and are never promoted into confirmed claims, timeline entries or exported facts automatically. Duplicates are suppressed. The briefing shows only pending suggestions whose original source still verifies against the quote.

**Review entire case locally:** Following one explicit confirmation, the same loopback Ollama service may review eligible indexed case documents one at a time. Progress is stored as source hashes and statuses only in the case-private working area. You can pause, resume and explicitly retry failed sources. Visiting a page never initiates analysis. Processing is bounded to 300 locally indexed sources; each source is verified against its original before inference and resulting hints always require individual review.

**Trust boundary:** The organizer controls its loopback connection, not the configuration or trustworthiness of the separately operated local Ollama service. Without Ollama, document intake, case organization and manual AI exchange remain available. No model inference is started automatically after import or page load.

## Automatic case narrative (unverified working draft)

The single-page interface now includes a collapsible **chronological working draft** with source-verified date mentions, operator-entered events, linked participants, open review questions and possible value differences. Explicitly role-labelled source lines such as “Sender:” or “Beklagter:” may be proposed as **unverified hints**; the organizer never creates a confirmed person record from them.

The selected-only lawyer export now includes `SACHVERHALT_ARBEITSSTAND.md`. Its narrative is limited to explicitly selected originals, excluding manual entries with mixed selected/unselected source links. Differing values appear only as **potential** review items where the operator previously grouped source-backed claims under the same topic and the exact original quotes still verify.

**Automatic related-document grouping:** Up to 120 already indexed originals are checked for explicitly labelled court/case reference numbers. Exact matching references, after only whitespace/case normalization, are shown on the **same simple page** as possible document groups, with source ID, filename, page and literal source quotation. Dates within a group remain unverified timeline hints. This does not prove that the documents actually belong to the same proceeding; unindexed, unreadable and tampered originals are excluded. No fuzzy linkage or model judgment is involved.

The lawyer handoff's `SACHVERHALT_ARBEITSSTAND.md` now includes these clearly qualified grouping suggestions. When exporting only part of a case, links are rebuilt solely from explicitly selected originals, so unselected filenames, quotes or IDs are not disclosed.

**Limits:** A date mention is not an established event, and a document role label is not proof of legal status. The tool cannot determine truth, culpability or deadlines. The draft is bounded, not necessarily complete, and read-only. The existing registers change only through explicitly requested actions.

## Case overview and lawyer-ready handoff

The simple page includes a **source-grounded case briefing** with document
counts, pending manual reviews, candidate date mentions and suggested next
actions. It neither determines procedural facts nor calculates legal deadlines;
date hints are unverified.

A deliberately initiated local export additionally contains
`ANWALT_START_HERE.md`, explaining reading order, evidence IDs and questions
for the operator or qualified counsel to verify.

**Export boundary:** Only explicitly selected originals and linked register,
timeline, person, task, claim and provenance records are included. Unlinked
records are excluded. Free-text entries may still contain sensitive details and
must be reviewed before any handoff.

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
