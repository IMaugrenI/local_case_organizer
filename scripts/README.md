# Script launcher map

This repository now exposes a sorted launcher layout by operating system.

## Preferred script layout

- `scripts/linux/` — shell launchers for Linux
- `scripts/windows/` — PowerShell launchers for Windows
- `scripts/macos/` — `.command` launchers for macOS

## Runtime truth

The runtime truth remains:

```bash
python run.py ...
```

The OS-specific script folders only contain thin wrappers.

## Sorted launcher parity

The sorted folders now cover these common launchers:

- `setup`
- `ui`
- `check`
- `status`
- `doctor`
- `import`
- `build-register`
- `build-timeline`
- `export-package`
- `start_here`

## Compatibility note

The older flat script files are still kept for compatibility and existing docs.

The sorted OS folders are the preferred structure going forward.
