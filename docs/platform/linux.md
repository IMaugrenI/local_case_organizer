# Linux

## Preferred starter path

```bash
bash scripts/linux/start_here.sh
```

## Thin wrapper folder

Linux shell launchers live under:

```text
scripts/linux/
```

## Typical operator path

```bash
python run.py setup
python run.py ui
python run.py check
python run.py status
python run.py doctor
```

## Notes

- Linux wrappers call the Python runtime truth
- the browser UI is the preferred normal-user front door
- backward-compatible root shell launchers still exist under `scripts/`
