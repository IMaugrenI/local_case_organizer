# Install and first test

This file is the shortest practical path for a fresh local download.

## 1. Get the repository

Clone it or download it from GitHub, then enter the repository folder.

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
```

## 2. Use the easiest start path

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

## 3. What should happen

The repository should:

1. prepare the local workspace
2. open the local browser UI

## 4. First real test in the browser

Use this simple sequence:

1. upload one or two small test files into the inbox
2. run import
3. build the register
4. build the timeline
5. add one entity row
6. mark one register row with `selected_for_export = yes`
7. build the export package

## 5. What counts as success

A good first test means:

- the browser UI opens locally
- the inbox accepts files
- import creates originals and provenance data
- register rows appear
- timeline rows can be edited
- entities can be edited
- export package creates a folder, ZIP, and manifest

## 6. If something fails

Run:

```bash
python run.py doctor
python run.py status
```

Then fix the first failing item before doing anything else.

## 7. Best first local test style

Do not begin with your most sensitive real data.

Begin with a tiny local test set first, confirm the flow works, then switch to real local material.
