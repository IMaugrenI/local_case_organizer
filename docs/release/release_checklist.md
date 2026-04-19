# Release checklist

Use this before calling a public release good enough for normal users.

## Basic repo checks

- README still matches the real start path
- `INSTALL_AND_FIRST_TEST.md` still matches the real start path
- `docs/guides/beginner_quickstart.md` still matches the browser UI
- no private or local test data is committed

## Smoke path

- fresh local clone works
- `scripts/linux/start_here.sh`, `scripts/windows/start_here.ps1`, and `scripts/macos/start_here.command` work on the intended platforms
- browser UI opens
- one small file can be imported
- register can be built
- timeline can be built
- entities can be edited
- export package creates folder, ZIP, and manifest

## User-facing truth

- error messages are understandable
- the next-step hints still make sense
- the main path works without reading deep internal docs

## Final rule

If a normal first-time user would still need to guess the next step, the release is not ready enough.
