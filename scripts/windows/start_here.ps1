$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $RepoRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
    $PythonArgs = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = "python"
    $PythonArgs = @()
} else {
    Write-Error "Python 3.11+ was not found. Install Python and make either 'py' or 'python' available."
    exit 1
}

& $PythonCommand @PythonArgs -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python 3.11 or newer is required. Check the installed Python version."
    exit 1
}

& $PythonCommand @PythonArgs run.py setup
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $PythonCommand @PythonArgs run.py ui
exit $LASTEXITCODE
