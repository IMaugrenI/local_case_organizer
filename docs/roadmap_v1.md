# local_case_organizer — V1 roadmap

## Goal

Build a neutral, local-first dossier organizer that helps users turn chaotic case documents into a reviewable working set.

## V1 scope

### 1. Repository truth and boundaries
- neutral public core only
- no real case data in the repository
- no hidden cloud path
- local/private overlays stay outside git

### 2. Import and original preservation
- import folder model
- originals remain preserved
- no silent overwrite or mutation of originals
- stable import manifest

### 3. File identity and provenance
- stable file IDs
- sha256 hash per file
- import timestamp
- original filename
- source location metadata

### 4. Register generation
- document register output
- relative path and category
- provenance-aware fields
- status markers for review

### 5. Timeline generation
- timeline CSV or similar output
- event date
- linked file IDs
- note field for neutral summaries

### 6. Export package
- export-ready case package
- neutral structure for advisory or legal handoff
- register + timeline + selected files

## Explicitly out of scope for early V1
- legal advice
- automatic legal scoring
- cloud inference
- hidden sync features
- guaranteed compliance claims

## Later candidates
- optional local OCR
- optional local AI suggestion layer
- profile overlays for different use contexts
- richer export templates
