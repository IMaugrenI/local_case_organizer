# Start here

This is the shortest path from a fresh clone to an organized local case and a clean handoff package.

> German version: [START_HERE_DE.md](START_HERE_DE.md)

## What this product is for

Bring a messy collection of local documents into one understandable case:

1. add documents
2. bring them into the case
3. review and group them
4. build a timeline
5. connect people and organizations
6. create a handoff package

Everything is designed to stay local. This tool organizes material; it does **not** decide what is legally correct, important or admissible.

## What you need

- Python 3.11+ (`py` or `python` on Windows)
- a local browser
- enough disk space for copied originals and handoff packages

## First start

### Linux

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
bash scripts/linux/start_here.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
.\scripts\windows\start_here.ps1
```

### macOS

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
./scripts/macos/start_here.command
```

The local browser page opens and shows the next useful step.

Windows: Run the `.ps1` file inside Windows PowerShell. PowerShell 7 (`pwsh`) is not required. If local script execution is blocked by an organization policy, do not silently bypass it.

The starter requires Python 3.11+. macOS `.command` files are tracked as executable files in the repository.


## Your first useful result

For a safe test, use synthetic/demo documents rather than real sensitive material.

A normal first journey is:

1. **Add documents**
2. **Add waiting files to this case**
3. **Create document overview**
4. review the files and mark the ones you want in the handoff
5. **Create timeline** and add at least one event if useful
6. add people or organizations if useful
7. **Create handoff package**

**Successful end result:** you have a local package containing the selected material, while the organizer still keeps the local working structure and traceability.

## If something does not work

The browser page shows a plain-language message and keeps technical details under **More options & technical details**.

Choose **Check for problems** there.

From the terminal:

```bash
python run.py doctor
```

If a file was changed after import, the export may stop rather than silently hand off a changed file. That is an integrity safeguard.

## Privacy and trust

Real case material can be sensitive.

Do not publish real case files, handoff packages, screenshots with personal information or private local paths in public GitHub issues.

Read [SECURITY.md](SECURITY.md) before using real sensitive material.

## Stop and come back later

The browser UI runs in the terminal process. Stop it with `Ctrl+C`.

Later run the same `start_here` launcher or:

```bash
python run.py ui
```

Your local case files remain in the ignored local workspace.

## Real-life example

See [docs/guides/USER_JOURNEY.md](docs/guides/USER_JOURNEY.md) for a complete case-to-handoff example and a realistic integrity-failure path.

## More detail

- [Beginner guide](docs/guides/beginner_quickstart.md)
- [Install and first test](docs/guides/install_and_first_test.md)
- [Commands](docs/reference/commands.md)
- [Release checklist](docs/release/release_checklist.md)
