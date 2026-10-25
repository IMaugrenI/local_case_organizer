# Productization roadmap

This file is the preferred sorted mirror of `docs/02_productization_roadmap.md`.

## Goal

Turn `local_case_organizer` from a good repository into a local end-user product that normal people can operate without living in the terminal.

## Product target

A user should be able to:

1. download the project
2. run the starter path
3. see a browser UI
4. add files
5. import them
6. build a register
7. build a timeline
8. export a handoff package

## Phase 1 — front door and basic workflow

Status: already started.

Target:

- local browser UI as the main front door
- setup through `start_here`
- inbox upload in the browser
- import button
- register button
- timeline button
- export button
- simple status cards
- next-step guidance

## Phase 2 — dossier editing layer

Target:

- editable register fields in the browser
- editable timeline rows in the browser
- visible document-group assignment
- visible export selection state
- file-to-event linking
- entities / people / institutions layer

## Phase 3 — export polish

Target:

- export only selected records
- export manifest
- zipped handoff package
- clearer delivery summary
- visible export history

## Phase 4 — cross-platform polish

Target:

- same behavior on Windows, Linux, and macOS
- clearer path-opening behavior
- better file-upload feedback
- friendlier error messages
- release-ready starter paths

## Phase 5 — release mode

Target:

- GitHub releases
- simple download package
- starter files per operating system
- short offline user guide inside the release package


## CASE-A1 (development branch) – case workspaces, provenance and links

- Legacy single-case workspace remains the default without migration.
- Explicit create-case/list-cases and --case select private, isolated workspaces.
- UI runs for one selected case per process; it does not silently switch scopes.
- Verify-integrity is manual only; source originals are never modified.
- A local append-only journal records verification results by file ID (no file contents).
- Evidence map displays only manually entered document-event-entity links.
- These are development features, not an operator acceptance or legal assessment.


## CASE-A2 (development branch) – provenance-based timeline suggestions

- Explicit \`python run.py [--case ID] propose-events\` and browser button.
- Reads only verified, registered, imported originals (.txt/.md/.csv/.eml, UTF-8)
  under a strict per-file byte limit; does not OCR, invoke an LLM or use the network.
- Extracts unverified YYYY-MM-DD and DD.MM.YYYY date mentions with source file ID,
  line number, excerpt, and deterministic suggestion ID.
- A user must **explicitly accept** a suggestion to append a draft timeline row.
  Before writing, the exact source is read and hash-checked again.
- Detects identical-content hashes across imported, scanned text items as
  a review hint. No automatic claims about truth, legality or completeness.
- Existing timelines, original files, imports, exports and legacy workspace
  remain in place; accepted events use the existing timeline CSV format.
- No private files, proposal excerpts or original source paths are committed
  to GitHub. This package is not the final acceptance.


## CASE-A3/A4 (development branch) – Local PDF/OCR index and sourced claims

- Extraction is **explicit**, opt-in, and scoped to a case's verified imported
  original: \`python run.py --case <id> index-document <DOC-ID> [--ocr]\`.
  The default legacy workspace remains available without \`--case\`.
- Supported local plaintext: UTF-8 TXT/MD/CSV/EML. PDFs use installed
  \`pdftotext\` (preferred) or optional Python \`pypdf\`.
  OCR requires explicit \`--ocr\` and preinstalled \`tesseract\`; scanned
  PDFs also require \`pdftoppm\`. No tool installs or network calls occur.
- The indexed derivative is a bounded JSON document under the existing ignored
  \`data/working/text_index/\` scoped to the selected case. The raw original is
  never altered or committed. Per-file size, page count, text and execution
  duration are bounded. Search verifies the original hash and excludes stale
  indexes: \`python run.py --case <id> search-text "needle"\`.
- Source-linked claims contain file ID, exact quote, page reference, a separate
  human-entered statement, and manual review status.
  Creating/reviewing a claim verifies the original source and matches the
  quote to the indexed page verbatim. Reviewed means a human reviewed the
  record; it does **not** certify truth or legal conclusions.
- Claims appear in the evidence graph and, when a user explicitly builds
  a handoff export, in \`claims.csv\`; private text-index derivatives are
  never included in exports by default.
- No server beyond the existing local browser UI, no forced dependencies,
  no cloud LLM, no automatic legal evaluation, no production installation.


## CASE-A5 (development) – manually grouped claim comparison

- Each comparison links an existing claim ID, operator-supplied topic key,
  explicitly selected date / decimal amount / plain text kind and value.
- Cross-document differences are flagged only for **two or more different
  source documents** and distinct normalized values under the same topic.
- No claims are automatically edited or pronounced false.
- Adding a link checks that the claim's original hash and exact quote still
  match the existing indexed source. No OCR/LLM or external services are called.
- Comparison data are kept in the selected local case register directory,
  never in GitHub. \`python run.py [--case ID] compare-claims\` is read-only.
- Existing case, source register, claim and export data remain undisturbed.


## CASE-A6 (development) – metadata-only local edit journal

- Atomic CSV replacements with two-phase \`prepared\` / \`committed\` journal
  entries for the existing register, timeline, entities, claims and comparison
  work areas. Routine generation of the register/timeline uses the same writer.
- Only timestamps, table area, affected row count and SHA-256 digests are
  stored; personal text, source originals and credentials are not copied.
- \`python run.py [--case ID] audit-history\` and a read-only UI panel show
  completed changes. No local username is asserted (there is no login system).
- A prepared-only record may remain after a power failure; it is **not** reported
  as committed.
- The journal has a size limit and never deletes entries automatically.
- This is *not* a signed or tamper-proof compliance trail and does not store
  earlier full document versions. Multi-process serialization is not guaranteed.
  Final acceptance remains separate at the end of expansion.
