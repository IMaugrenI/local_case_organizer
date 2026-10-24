# Security and privacy

`local_case_organizer` is designed for local organization of potentially sensitive case files.

## Keep real case data local

Do not commit or publish:

- files from `data/`
- files from `exports/`
- real case documents
- screenshots containing names, addresses, account numbers, case numbers, or private correspondence
- absolute local paths that reveal usernames or private folder structures
- generated ZIP/export packages
- secrets or credentials

The repository `.gitignore` excludes the normal runtime data locations, but users are still responsible for checking public commits and screenshots.

## Import integrity

Imports:

- copy source files into a dedicated local originals area
- assign a unique import batch and file ID
- record SHA-256 for imported originals
- reject/skip source-tree symlink targets that escape the explicitly selected source root

The internal provenance record may contain the original local source path for local traceability.

## Export privacy

Normal handoff exports use a sanitized provenance view and intentionally exclude absolute local source paths.

Selected original files are resolved back under the managed `data/originals/` root and hash-checked against provenance before they are copied into an export.

A mismatch is treated as an integrity failure rather than silently exporting changed data.

## What this does not guarantee

This project does not guarantee:

- legal correctness
- GDPR compliance for every possible deployment or dataset
- evidentiary admissibility
- malware scanning of imported documents
- encryption at rest

If your use case requires those guarantees, add the appropriate operational controls outside this repository.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting where available. Do not place real case data, private paths, or secrets in public issues.
