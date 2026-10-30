# Install and first test

This file is the shortest practical path for a fresh local download. No package installation is required for the normal `run.py` path; the repository adds its local `src/` directory itself.

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
.\scripts\windows\start_here.ps1
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

1. choose or create a local case in the existing browser
2. select or drop one or two *synthetic* small files, deliberately starting the bounded local import
3. use **Continue processing** only if the page reports pending work
4. open the document register, filter or change pages, and explicitly review the files
5. optionally create a manual event, task, or participant linked to a source
6. select just one test original for export
7. use **Check handoff** to inspect selected-only warnings and confirm the local ZIP export

## 5. What counts as success

A good first test means:

- the browser UI opens locally
- the inbox accepts files
- deliberate import creates immutable originals and provenance data
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

## Release-ready versus development-tested

GitHub CI checks the Python CLI and targeted Windows/macOS launchers.
Only an actual target-system run can prove browser interaction, optional
offline PDF/OCR dependencies, OS security prompts, file permissions and
full export behavior. The operator records these in
[the release checklist](../release/release_checklist.md).
