$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $RepoRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = "python"
} else {
    Write-Error "Python 3.11+ was not found. Install Python and make either 'py' or 'python' available."
    exit 1
}

& $PythonCommand run.py setup
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $PythonCommand run.py ui
exit $LASTEXITCODE
