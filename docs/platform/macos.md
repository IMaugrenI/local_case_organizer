# macOS

## Preferred starter path

```bash
./scripts/macos/start_here.command
```

## Thin wrapper folder

macOS launchers live under:

```text
scripts/macos/
```

## Typical operator path

```bash
python3 run.py setup
python3 run.py ui
python3 run.py check
python3 run.py status
python3 run.py doctor
```

## Notes

- macOS launchers call the Python runtime truth
- the browser UI is the preferred normal-user front door
- backward-compatible root `.command` launchers still exist under `scripts/`
