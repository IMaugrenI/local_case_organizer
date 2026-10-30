# macOS launcher path

Preferred macOS launcher folder:

```bash
scripts/macos/
```

## Recommended start path

```bash
./scripts/macos/start_here.command
```

## Other common commands

```bash
./scripts/macos/setup.command
./scripts/macos/check.command
./scripts/macos/status.command
./scripts/macos/doctor.command
./scripts/macos/import.command
```

## Runtime truth

The runtime truth remains:

```bash
python run.py ...
```

## Executable files and operating limits

The existing `.command` launchers are tracked as executable Git files;
this is required for their `./scripts/macos/...` invocation. The
`start_here.command` script checks Python 3.11+ and aborts on setup
failure before opening a browser. No installer or alternate runtime is
created. Local OS security prompts and the real GUI still need target-device
verification; a macOS CI CLI check is not a full macOS acceptance.
