# Commands

This file is the preferred sorted mirror of `docs/commands.md`.

## Fastest beginner path

If you want the shortest safe path:

```bash
bash scripts/linux/start_here.sh
```

Equivalent entry points:

- PowerShell: `pwsh ./scripts/windows/start_here.ps1`
- macOS: `./scripts/macos/start_here.command`

That path runs setup and opens the local browser UI.

## Primary command path

Run all commands from the repository root.

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

## Thin wrapper path

The runtime truth is `python run.py ...`.

Thin wrappers are available for the primary operator commands:

- Linux: `scripts/linux/*.sh`
- PowerShell: `scripts/windows/*.ps1`
- macOS: `scripts/macos/*.command`

## Safety markers

- SAFE: `start_here`, `setup`, `ui`, `check`, `status`, `doctor`, `import`, `build-register`, `build-timeline`, `export-package`
- ADVANCED: `import --source /path/to/files`
- DESTRUCTIVE: none in the current public V1 path

## Local testing rule

Private case material belongs only in ignored local paths and must not be committed.
