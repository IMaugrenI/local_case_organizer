# Windows launcher path

The **existing** PowerShell scripts under `scripts/windows/` are the only
Windows launch path. Open Windows PowerShell 5.1 or PowerShell 7 inside
the repository directory; Python 3.11+ is required.

```powershell
.\scripts\windows\start_here.ps1
```

Optional PowerShell 7 invocation:

```powershell
pwsh -File ./scripts/windows/start_here.ps1
```

Additional existing commands:

```powershell
.\scripts\windows\setup.ps1
.\scripts\windows\doctor.ps1
.\scripts\windows\status.ps1
.\scripts\windows\import.ps1
```

These wrappers select Python 3 explicitly when the Windows `py`
launcher exists, check its version, and then call the existing `run.py`.
A nonzero `doctor` exit code means the runtime checks did not pass.

If your computer blocks PowerShell scripts by system policy, follow
your administrator's guidance rather than silently bypassing controls.

GitHub CI validates setup/doctor/help on a Windows runner, **not**
interactive UI, OCR, local case persistence, or an installation on the
actual target device.
