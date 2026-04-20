$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $RepoRoot
python run.py build-timeline @args
