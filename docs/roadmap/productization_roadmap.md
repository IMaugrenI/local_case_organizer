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
