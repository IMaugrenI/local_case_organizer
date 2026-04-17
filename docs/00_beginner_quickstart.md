# Beginner quickstart

This guide is for people who want the shortest safe path.

## What this repo is

`local_case_organizer` helps you turn a pile of local case files into a cleaner dossier.

You do **not** need to understand the whole repo first.

## Fastest safe path

### Linux

```bash
bash scripts/start_here.sh
```

### Windows PowerShell

```powershell
pwsh ./scripts/start_here.ps1
```

### macOS

```bash
./scripts/start_here.command
```

## What happens

The start-here path does two safe first steps:

1. prepares the local folders you need
2. shows your current local status

After that, your normal next path is:

```bash
python run.py import
python run.py build-register
python run.py build-timeline
python run.py export-package
```

## What success looks like

You should end up with:

- a ready local workspace
- an inbox folder for dropped files
- a simple status summary

## If something fails

Run:

```bash
python run.py doctor
```

Then read the printed checks and fix the first failing item.
