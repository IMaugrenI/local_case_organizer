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

Early public scaffold.

The first goal is a clean, truthful repo shape before feature growth.
