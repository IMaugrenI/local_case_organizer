# Release checklist

Use this before calling a public release good enough for normal users.

## Basic repo checks

- README still matches the real start path
- `docs/guides/install_and_first_test.md` still matches the real start path
- `docs/guides/beginner_quickstart.md` still matches the browser UI
- `docs/reference/commands.md` still matches the real command surface
- no private or local test data is committed

## Smoke path

- fresh local clone works
- the sorted launchers under `scripts/linux/`, `scripts/windows/`, and `scripts/macos/` still work on the intended platforms
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
