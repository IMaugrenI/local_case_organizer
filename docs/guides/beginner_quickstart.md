# Beginner quickstart

This guide is for people who want the shortest safe path.

## What this repo is

`local_case_organizer` helps you turn a pile of local case files into a cleaner dossier.

You do **not** need to understand the whole repo first.

## Fastest safe path

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

## What happens

The start-here path now does two simple things:

1. prepares the local folders you need
2. opens the local browser UI

Inside the browser UI you can then use the main safe actions for:

- upload files to the inbox
- import inbox files
- build register
- edit register fields
- build timeline
- edit timeline rows
- edit entities / people / institutions
- build export package

## What success looks like

You should end up with:

- a ready local workspace
- an inbox folder for dropped files
- a local browser UI on your machine
- a simple button-driven workflow
- a dossier package with a ZIP handoff output

## Simple normal path

- upload or drop files into the inbox
- import the inbox files
- build the register
- review the important files and mark `selected_for_export = yes`
- build or edit the timeline
- add important people or institutions in the entities table
- build the export package

## If something fails

Run:

```bash
python run.py doctor
```

Then read the printed checks and fix the first failing item.
