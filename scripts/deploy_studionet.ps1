$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
# Prefer the repository's Python 3.12 environment; fall back to the native
# launcher. The guard itself resolves only the repository-local genlayer.cmd.
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { $python = 'py'; $pythonArgs = @('-3.12') } else { $pythonArgs = @() }
& $python @pythonArgs scripts/network_guard.py --deploy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
